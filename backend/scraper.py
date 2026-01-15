from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random

def setup_driver():
    """Setup Selenium WebDriver with headless Chrome"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_zepto(items, location='Pune'):
    """Scrape prices from Zepto"""
    results = []

    print("Starting Zepto scraper...")
    try:
        driver = setup_driver()
        print("Selenium WebDriver for Zepto initialized.")

        for item in items:
            try:
                # Navigate to Zepto search
                print(f"Scraping Zepto for item: Entered Zepto")
                search_url = f"https://www.zepto.com/search?query={item.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(random.uniform(2, 4))


                # Wait for products to load
                print(f"Scraping Zepto for item: Waiting for products to load")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card"]'))
                )
                print("products loaded successfully")

                # Get first product
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                product_card = soup.find('div', {'data-testid': 'product-card'})

                if product_card:
                    name_elem = product_card.find('h4')
                    price_elem = product_card.find('span', string=lambda x: x and '₹' in str(x))

                    name = name_elem.text.strip() if name_elem else item
                    price_text = price_elem.text.strip() if price_elem else '0'
                    price = float(price_text.replace('₹', '').replace(',', '').strip())

                    results.append({
                        "name": name,
                        "price": price,
                        "available": True,
                        "url": search_url
                    })
                else:
                    results.append({
                        "name": item,
                        "price": 0,
                        "available": False,
                        "url": search_url
                    })
            except Exception as e:
                print(f"Error scraping Zepto for {item}: {e}")
                results.append({
                    "name": item,
                    "price": 0,
                    "available": False,
                    "url": ""
                })

        driver.quit()

    except Exception as e:
        print(f"Zepto scraper error: {e}")

    return {
        "items": results,
        "delivery_fee": 0 if sum(item['price'] for item in results) > 199 else 25,
        "platform_fee": 2
    }
def scrape_blinkit(items, location='Pune'):
    """Scrape prices from Blinkit"""
    results = []

    try:
        driver = setup_driver()

        for item in items:
            try:
                search_url = f"https://blinkit.com/s/?q={item.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(random.uniform(2, 4))

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'Product__UpdatedC'))
                )

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                product = soup.find('div', class_='Product__UpdatedC')

                if product:
                    name_elem = product.find('div', class_='Product__UpdatedTitle')
                    price_elem = product.find('div', class_='Product__UpdatedPrice')

                    name = name_elem.text.strip() if name_elem else item
                    price_text = price_elem.text.strip() if price_elem else '0'
                    price = float(price_text.replace('₹', '').replace(',', '').strip())

                    results.append({
                        "name": name,
                        "price": price,
                        "available": True,
                        "url": search_url
                    })
                else:
                    results.append({
                        "name": item,
                        "price": 0,
                        "available": False,
                        "url": search_url
                    })
            except Exception as e:
                print(f"Error scraping Blinkit for {item}: {e}")
                results.append({
                    "name": item,
                    "price": 0,
                    "available": False,
                    "url": ""
                })

        driver.quit()

    except Exception as e:
        print(f"Blinkit scraper error: {e}")

    return {
        "items": results,
        "delivery_fee": 0 if sum(item['price'] for item in results) > 199 else 25,
        "platform_fee": 0
    }
def scrape_instamart(items, location='Pune'):
    """Scrape prices from Swiggy Instamart"""
    results = []

    # Instamart requires location/login, using mock data for demo
    # In production, implement proper scraping with auth

    for item in items:
        # Mock pricing logic
        base_price = random.uniform(20, 200)
        results.append({
            "name": f"{item.title()} (Instamart)",
            "price": round(base_price, 2),
            "available": True,
            "url": f"https://www.swiggy.com/instamart/search?q={item}"
        })

    return {
        "items": results,
        "delivery_fee": 0 if sum(item['price'] for item in results) > 199 else 29,
        "platform_fee": 3
    }
def scrape_flipkart_minutes(items, location='Pune'):
    """Scrape prices from Flipkart Minutes"""
    results = []

    # Flipkart Minutes is location-based, using mock data for demo
    # In production, implement proper scraping

    for item in items:
        base_price = random.uniform(20, 200)
        results.append({
            "name": f"{item.title()} (Flipkart)",
            "price": round(base_price, 2),
            "available": True,
            "url": f"https://www.flipkart.com/search?q={item}"
        })

    return {
        "items": results,
        "delivery_fee": 0,
        "platform_fee": 5
    }
def scrape_all_platforms(items, location='Pune'):
    """Scrape all platforms and return consolidated results"""

    print(f"Scraping prices for {len(items)} items in {location}...")

    results = {
        "Zepto": scrape_zepto(items, location),
        "Blinkit": scrape_blinkit(items, location),
        "Instamart": scrape_instamart(items, location),
        "Flipkart Minutes": scrape_flipkart_minutes(items, location)
    }

    return results
# Mock function for testing without Selenium
def mock_scrape_all_platforms(items, location='Pune'):
    """Mock scraper for testing without browser automation"""

    # Sample mock data
    mock_prices = {
        "milk": {"Zepto": 56, "Blinkit": 58, "Instamart": 54, "Flipkart Minutes": 57},
        "bread": {"Zepto": 35, "Blinkit": 33, "Instamart": 36, "Flipkart Minutes": 34},
        "eggs": {"Zepto": 84, "Blinkit": 82, "Instamart": 85, "Flipkart Minutes": 83},
    }

    results = {}

    for platform in ["Zepto", "Blinkit", "Instamart", "Flipkart Minutes"]:
        platform_items = []

        for item in items:
            # Find closest match in mock data
            item_lower = item.lower()
            matched_key = None

            for key in mock_prices.keys():
                if key in item_lower or item_lower in key:
                    matched_key = key
                    break

            if matched_key and platform in mock_prices[matched_key]:
                price = mock_prices[matched_key][platform]
            else:
                price = random.uniform(20, 150)

            platform_items.append({
                "name": item,
                "price": round(price, 2),
                "available": True,
                "url": f"https://{platform.lower().replace(' ', '')}.com/search?q={item}"
            })

        delivery_fee = 0 if sum(i['price'] for i in platform_items) > 199 else 25
        platform_fee = {"Zepto": 2, "Blinkit": 0, "Instamart": 3, "Flipkart Minutes": 5}[platform]

        results[platform] = {
            "items": platform_items,
            "delivery_fee": delivery_fee,
            "platform_fee": platform_fee
        }

    return results