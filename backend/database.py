import sqlite3
from datetime import datetime, timedelta
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'prices.db')
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_product_platform
        ON price_history(product_name, platform)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON price_history(timestamp)
    ''')

    conn.commit()
    conn.close()
def save_price_history(product_name, platform, price):
    """Save price data to history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO price_history (product_name, platform, price)
            VALUES (?, ?, ?)
        ''', (product_name, platform, price))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving price history: {e}")
        return False
def get_price_trends(product_name, days=7):
    """Get price trends for a product"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute('''
            SELECT platform, AVG(price) as avg_price,
                   MIN(price) as min_price, MAX(price) as max_price,
                   COUNT(*) as data_points
            FROM price_history
            WHERE product_name = ? AND timestamp >= ?
            GROUP BY platform
        ''', (product_name, cutoff_date))

        results = cursor.fetchall()

        trends = {}
        for row in results:
            platform, avg_price, min_price, max_price, data_points = row
            trends[platform] = {
                "avg_price": round(avg_price, 2),
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "data_points": data_points
            }

        conn.close()
        return trends
    except Exception as e:
        print(f"Error getting price trends: {e}")
        return {}
def get_historical_comparison(product_name, platform, days=30):
    """Get historical price data for chart"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute('''
            SELECT DATE(timestamp) as date, AVG(price) as avg_price
            FROM price_history
            WHERE product_name = ? AND platform = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        ''', (product_name, platform, cutoff_date))

        results = cursor.fetchall()

        data = [{"date": row[0], "price": round(row[1], 2)} for row in results]

        conn.close()
        return data
    except Exception as e:
        print(f"Error getting historical data: {e}")
        return []
def cleanup_old_data(days=90):
    """Remove price data older than specified days"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute('''
            DELETE FROM price_history
            WHERE timestamp < ?
        ''', (cutoff_date,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count
    except Exception as e:
        print(f"Error cleaning up old data: {e}")
        return 0