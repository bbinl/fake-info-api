from flask import Flask, request, jsonify
import sys
import os
import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

# Vercel-এ হোস্ট করার জন্য প্রজেক্ট ফোল্ডার স্ট্রাকচার ঠিক করা
# Vercel-এর রুটে app.py ফাইলটি থাকবে, তাই sys.path এর প্রয়োজন নেই।

app = Flask(__name__)

# সকল দেশের তালিকা (Country Code, Country Name, URL Part)
countries_data = [
    {"code": "ar", "name": "argentina", "url_part": "argentina"},
    {"code": "am", "name": "armenia", "url_part": "armenia"},
    {"code": "au", "name": "australia", "url_part": "australia"},
    {"code": "at", "name": "austria", "url_part": "austria"},
    {"code": "bd", "name": "bangladesh", "url_part": "bangladesh"},
    {"code": "be", "name": "belgium", "url_part": "belgium"},
    {"code": "ba", "name": "bosnia and herzegovina", "url_part": "bosnia-herzegovina"},
    {"code": "br", "name": "brazil", "url_part": "brazil"},
    {"code": "bg", "name": "bulgaria", "url_part": "bulgaria"},
    {"code": "ca", "name": "canada", "url_part": "canada"},
    {"code": "cn", "name": "china", "url_part": "china"},
    {"code": "hr", "name": "croatia", "url_part": "croatia"},
    {"code": "cy", "name": "cyprus", "url_part": "cyprus"},
    {"code": "cz", "name": "czech republic", "url_part": "czech-republic"},
    {"code": "dk", "name": "denmark", "url_part": "denmark"},
    {"code": "eg", "name": "egypt", "url_part": "egypt"},
    {"code": "ee", "name": "estonia", "url_part": "estonia"},
    {"code": "fi", "name": "finland", "url_part": "finland"},
    {"code": "fr", "name": "france", "url_part": "france"},
    {"code": "ge", "name": "georgia", "url_part": "georgia"},
    {"code": "de", "name": "germany", "url_part": "germany"},
    {"code": "gb", "name": "great britain", "url_part": "united-kingdom"},
    {"code": "gr", "name": "greece", "url_part": "greece"},
    {"code": "hk", "name": "hong kong", "url_part": "hong-kong"},
    {"code": "hu", "name": "hungary", "url_part": "hungary"},
    {"code": "is", "name": "iceland", "url_part": "iceland"},
    {"code": "in", "name": "india", "url_part": "india"},
    {"code": "id", "name": "indonesia", "url_part": "indonesia"},
    {"code": "ir", "name": "iran", "url_part": "iran"},
    {"code": "il", "name": "israil", "url_part": "israil"},
    {"code": "it", "name": "italy", "url_part": "italy"},
    {"code": "jp", "name": "japan", "url_part": "japan"},
    {"code": "jo", "name": "jordan", "url_part": "jordan"},
    {"code": "kz", "name": "kazakhstan", "url_part": "kazakhstan"},
    {"code": "lv", "name": "latvia", "url_part": "latvia"},
    {"code": "lt", "name": "lithuania", "url_part": "lithunia"},
    {"code": "my", "name": "malaysia", "url_part": "malaysia"},
    {"code": "mx", "name": "mexico", "url_part": "mexico"},
    {"code": "md", "name": "moldova", "url_part": "moldova"},
    {"code": "mn", "name": "mongolia", "url_part": "mongolia"},
    {"code": "me", "name": "montenegro", "url_part": "montenegro"},
    {"code": "np", "name": "nepal", "url_part": "nepal"},
    {"code": "nl", "name": "netherlands", "url_part": "netherlands"},
    {"code": "nz", "name": "new zeland", "url_part": "new-zeland"},
    {"code": "ng", "name": "nigeria", "url_part": "nigeria"},
    {"code": "no", "name": "norway", "url_part": "norway"},
    {"code": "pe", "name": "peru", "url_part": "peru"},
    {"code": "ph", "name": "philippines", "url_part": "philippines"},
    {"code": "pl", "name": "poland", "url_part": "poland"},
    {"code": "pt", "name": "portugal", "url_part": "portugal"},
    {"code": "ro", "name": "romania", "url_part": "romania"},
    {"code": "ru", "name": "russia", "url_part": "russia"},
    {"code": "sa", "name": "saudi arabia", "url_part": "saudi-arabia"},
    {"code": "rs", "name": "serbia", "url_part": "serbia"},
    {"code": "sg", "name": "singapore", "url_part": "singapore"},
    {"code": "sk", "name": "slovakia", "url_part": "slovakia"},
    {"code": "si", "name": "slovenia", "url_part": "slovenia"},
    {"code": "za", "name": "south africa", "url_part": "south-africa"},
    {"code": "kr", "name": "south korea", "url_part": "south-korea"},
    {"code": "es", "name": "spain", "url_part": "spain"},
    {"code": "se", "name": "sweden", "url_part": "sweden"},
    {"code": "ch", "name": "switzerland", "url_part": "switzerland"},
    {"code": "tw", "name": "taiwan", "url_part": "taiwan"},
    {"code": "th", "name": "thailand", "url_part": "thailand"},
    {"code": "tr", "name": "turkey", "url_part": "turkey"},
    {"code": "us", "name": "usa", "url_part": "usa"},
    {"code": "ug", "name": "uganda", "url_part": "uganda"},
    {"code": "ua", "name": "ukraine", "url_part": "ukraine"},
    {"code": "ve", "name": "venezuela", "url_part": "venezuela"},
    {"code": "vn", "name": "vietnam", "url_part": "vietnam"}
]

def get_country_info(query):
    """
    দেশের নাম বা কোড খুঁজে বের করে এবং কাছাকাছি মিল খুঁজে বের করার চেষ্টা করে।
    """
    query = query.lower()
    
    # প্রথমে কোড বা নাম দিয়ে সরাসরি মিল খোঁজা
    for country in countries_data:
        if country["code"] == query or country["name"] == query:
            return country
    
    # যদি সরাসরি মিল না পাওয়া যায়, তাহলে সবচেয়ে কাছাকাছি মিল খোঁজা
    all_names = [c["name"] for c in countries_data]
    close_matches = get_close_matches(query, all_names, n=1, cutoff=0.6)
    if close_matches:
        match_name = close_matches[0]
        for country in countries_data:
            if country["name"] == match_name:
                return {"error": "not_found", "suggestion": country["name"]}
    
    return None

def scrape_data(url):
    """
    নির্দিষ্ট URL থেকে ডেটা স্ক্র্যাপ করে JSON হিসেবে ফেরত দেয়।
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # HTML টেবিল থেকে ডেটা পার্স করা
        table = soup.find('table', class_='table table-striped')
        if not table:
            return {"error": "ওয়েবসাইট থেকে ডেটা পাওয়া যায়নি।"}
            
        data = {}
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            
            # ডেটা এক্সট্র্যাক্ট করা
            for i in range(0, len(cols), 2):
                if len(cols) > i + 1:
                    key = cols[i].get_text(strip=True).replace(" ", "_").lower().strip()
                    value_tag = cols[i+1].find('span')
                    if value_tag:
                        value = value_tag.get_text(strip=True)
                        data[key] = value
                    else:
                        # ইমেলের মতো বিশেষ ক্ষেত্রে
                        email_tag = cols[i+1].find('a', class_='__cf_email__')
                        if email_tag:
                            # এখানে ইমেল ডিকোড করার জন্য JavaScript এর লজিক দরকার।
                            # যেহেতু এটি কঠিন, তাই আপাতত placeholder রাখা হলো।
                            data[key] = "Email obfuscated (unable to decode)"
                        else:
                            data[key] = cols[i+1].get_text(strip=True)

        return data
        
    except requests.exceptions.RequestException as e:
        return {"error": f"ওয়েবসাইট অ্যাক্সেস করতে সমস্যা হয়েছে: {str(e)}"}
    except Exception as e:
        return {"error": f"স্ক্র্যাপিং এর সময় একটি ত্রুটি হয়েছে: {str(e)}"}

@app.route('/api', methods=['GET'])
def api_handler():
    country_query = request.args.get('country', None)
    
    if not country_query:
        return jsonify({"error": "অনুগ্রহ করে 'country' প্যারামিটার দিন।", "usage": "উদাহরণ: /api?country=bd অথবা /api?country=bangladesh"}), 400

    country_info = get_country_info(country_query)

    if not country_info:
        # কোনো মিল পাওয়া যায়নি
        return jsonify({"error": "আপনার দেওয়া কান্ট্রিটি খুঁজে পাওয়া যায়নি।", "suggestion": None}), 404
    
    if "suggestion" in country_info:
        # কাছাকাছি একটি মিল পাওয়া গেছে
        return jsonify({"error": "আপনার দেওয়া কান্ট্রিটি খুঁজে পাওয়া যায়নি।", "suggestion": f"আপনি কি {country_info['suggestion']} খুঁজছেন?"}), 404

    # সফলভাবে কান্ট্রি খুঁজে পাওয়া গেছে
    url_part = country_info["url_part"]
    full_url = f"https://outputter.io/full-identity/{url_part}/"
    
    scraped_data = scrape_data(full_url)
    
    if "error" in scraped_data:
        return jsonify(scraped_data), 500
    else:
        return jsonify(scraped_data), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Identity Scraper API",
        "usage": "Use /api?country=<country_code_or_name> to get identity data",
        "example": "/api?country=bd or /api?country=bangladesh"
    })
    
# Vercel-এর জন্য `app` অবজেক্ট এক্সপোর্ট করা হয়
# if __name__ == '__main__':
#     app.run(debug=True)
