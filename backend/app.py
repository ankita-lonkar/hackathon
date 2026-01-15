from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from datetime import datetime
from scraper import scrape_all_platforms, mock_scrape_all_platforms
from database import init_db, save_price_history, get_price_trends
import traceback
app = Flask(__name__)
CORS(app)
# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)
# Initialize database
init_db()
def extract_items_with_ai(user_input):
    """Use Gemini to extract shopping items from natural language"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Print model name
        prompt = f"""
        Extract shopping items from this text: "{user_input}"
        Return ONLY a JSON array of items in this exact format:
        ["item1", "item2", "item3"]
        Rules:
        - Normalize quantities (e.g., "2 liters milk" → "milk 2L", "dozen eggs" → "eggs 12")
        - Keep it simple and searchable
        - Remove unnecessary words
        - Common formats: "milk 1L", "bread brown", "eggs 12", "rice 5kg"
        Examples:
        Input: "I need 2 liters of milk, brown bread and a dozen eggs"
        Output: ["milk 2L", "bread brown", "eggs 12"]
        Input: "Get me Amul butter, 1kg rice and cold coffee"
        Output: ["amul butter", "rice 1kg", "cold coffee"]
        Return ONLY the JSON array, nothing else.
        """
        response = model.generate_content(prompt)
        print("AI extraction response:", response.text)
        items_json = response.text.strip()
        # Clean response
        items_json = items_json.replace('```json', '').replace('```', '').strip()
        items = json.loads(items_json)
        return items
    except Exception as e:
        print(f"AI extraction error: {e}")
        # Fallback: basic splitting
        return [item.strip() for item in user_input.split(',')]
def match_products_with_ai(user_item, scraped_products):
    """Use AI to match user's generic search with specific product names"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        product_list = "\n".join([f"{i+1}. {p['name']} - ₹{p['price']}"
                                  for i, p in enumerate(scraped_products)])
        prompt = f"""
        User is searching for: "{user_item}"
        Available products:
        {product_list}
        Return the NUMBER (1-{len(scraped_products)}) of the BEST matching product.
        Consider:
        - Brand relevance
        - Size/quantity match
        - Product type similarity
        Return ONLY the number, nothing else.
        If no good match, return "0".
        """
        response = model.generate_content(prompt)
        match_num = int(response.text.strip())
        if match_num > 0 and match_num <= len(scraped_products):
            return scraped_products[match_num - 1]
        return scraped_products[0] if scraped_products else None
    except Exception as e:
        print(f"AI matching error: {e}")
        return scraped_products[0] if scraped_products else None

def generate_shopping_insights(comparison_data, price_trends):
    """Generate AI-powered shopping insights"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Analyze this shopping comparison data and provide insights:
        {json.dumps(comparison_data, indent=2)}
        Price trends (if available):
        {json.dumps(price_trends, indent=2)}
        Generate insights in JSON format:
        {{
            "recommendation": "Which platform to use and why (1-2 sentences)",
            "price_trend": "Are prices rising/falling/stable? (1 sentence)",
            "savings_tip": "How to maximize savings (1 sentence)",
            "smart_suggestion": "Should they combine orders or buy from one platform? Why?"
        }}
        Be concise, practical, and money-saving focused.
        Return ONLY the JSON object.
        """
        response = model.generate_content(prompt)
        insights_json = response.text.strip()
        insights_json = insights_json.replace('```json', '').replace('```', '').strip()
        insights = json.loads(insights_json)
        return insights
    except Exception as e:
        print(f"AI insights error: {e}")
        return {
            "recommendation": "Compare prices above to find the best deal.",
            "price_trend": "Price data unavailable.",
            "savings_tip": "Consider delivery fees when choosing a platform.",
            "smart_suggestion": "Buy all items from the cheapest overall platform to save on delivery."
        }
#working fine        
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# extract items is working fine    
@app.route('/api/extract-items', methods=['POST'])
def extract_items():
    """Extract items from natural language input"""
    try:
        data = request.json
        user_input = data.get('input', '')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        items = extract_items_with_ai(user_input)
        return jsonify({"items": items, "count": len(items)})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/compare-prices', methods=['POST'])
def compare_prices():
    """Compare prices across all platforms"""
    print("*********Received price comparison request**********")
    try:
        data = request.json
        items = data.get('items', [])
        location = data.get('location', 'Pune')
        if not items:
            return jsonify({"error": "No items provided"}), 400
        # Scrape prices from all platforms
        all_results = mock_scrape_all_platforms(items, location)
        print("*************", all_results)
        # Calculate total costs per platform
        platform_totals = {}
        for platform_name, platform_data in all_results.items():
            items_total = sum(item['price'] for item in platform_data['items']
                            if item['price'] > 0)
            delivery_fee = platform_data.get('delivery_fee', 0)
            platform_fee = platform_data.get('platform_fee', 0)
            total = items_total + delivery_fee + platform_fee
            platform_totals[platform_name] = {
                "items_total": items_total,
                "delivery_fee": delivery_fee,
                "platform_fee": platform_fee,
                "total": total,
                "items": platform_data['items']
            }
        # Find cheapest platform
        cheapest_platform = min(platform_totals.items(),
                              key=lambda x: x[1]['total'])[0]
        # Save price history
        for platform, data in platform_totals.items():
            for item in data['items']:
                if item['price'] > 0:
                    save_price_history(item['name'], platform, item['price'])
        # Get price trends
        price_trends = {}
        for item_name in [item['name'] for platform in platform_totals.values()
                         for item in platform['items'] if item['price'] > 0]:
            price_trends[item_name] = get_price_trends(item_name)
        # Generate AI insights
        insights = generate_shopping_insights(platform_totals, price_trends)
        return jsonify({
            "platforms": platform_totals,
            "cheapest_platform": cheapest_platform,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Conversational AI assistant"""
    try:
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', {})
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        You are a smart shopping assistant for Indian quick-commerce platforms.
        User question: "{user_message}"
        Context (previous comparison data):
        {json.dumps(context, indent=2)}
        Provide a helpful, concise response (2-3 sentences max).
        Focus on:
        - Price trends
        - Money-saving tips
        - Platform recommendations
        - Product availability
        Be conversational and friendly.
        """
        response = model.generate_content(prompt)
        answer = response.text.strip()
        return jsonify({
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/substitute', methods=['POST'])
def suggest_substitute():
    """Suggest product substitutes"""
    try:
        data = request.json
        product_name = data.get('product', '')
        reason = data.get('reason', 'out of stock')
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Product: "{product_name}"
        Issue: {reason}
        Suggest 2-3 substitute products available in Indian quick-commerce.
        Return JSON format:
        {{
            "substitutes": [
                {{"name": "Product 1", "reason": "Why it's a good substitute"}},
                {{"name": "Product 2", "reason": "Why it's a good substitute"}}
            ]
        }}
        Return ONLY the JSON.
        """
        response = model.generate_content(prompt)
        suggestions_json = response.text.strip()
        suggestions_json = suggestions_json.replace('```json', '').replace('```', '').strip()
        suggestions = json.loads(suggestions_json)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
