from flask import Flask, request, jsonify, render_template_string
import sys
import os
import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

app = Flask(__name__)

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
    query = query.lower()
    for country in countries_data:
        if country["code"] == query or country["name"] == query:
            return country
    all_names = [c["name"] for c in countries_data]
    close_matches = get_close_matches(query, all_names, n=1, cutoff=0.6)
    if close_matches:
        match_name = close_matches[0]
        for country in countries_data:
            if country["name"] == match_name:
                return {"error": "not_found", "suggestion": country["name"]}
    return None

def parse_table_data(table):
    data = {}
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['th', 'td'])
        for i in range(0, len(cols), 2):
            if len(cols) > i + 1:
                key_tag = cols[i]
                value_tag = cols[i+1]
                key = key_tag.get_text(strip=True).replace(" ", "_").replace("(", "").replace(")", "").replace("'", "").lower().strip()
                value = None
                span_tag = value_tag.find('span')
                if span_tag:
                    value = span_tag.get_text(strip=True)
                if not value:
                    img_tag = value_tag.find('img')
                    if img_tag and img_tag.parent.get_text(strip=True):
                        value = img_tag.parent.get_text(strip=True)
                    else:
                        email_tag = value_tag.find('a', class_='__cf_email__')
                        if email_tag:
                            value = "Email obfuscated (unable to decode)"
                        else:
                            value = value_tag.get_text(strip=True)
                data[key] = value if value else None
    return data

def scrape_data(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        scraped_data = {}
        card_sections = soup.find_all('div', class_='card')
        for card in card_sections:
            header_tag = card.find('div', class_='card-header')
            table_tag = card.find('table', class_='table table-striped')
            if header_tag and table_tag:
                section_name = header_tag.find('strong').get_text(strip=True)
                table_data = parse_table_data(table_tag)
                scraped_data[section_name.replace(" ", "_")] = table_data
        if not scraped_data:
            return {"error": "ওয়েবসাইট থেকে ডেটা পাওয়া যায়নি।"}
        return scraped_data
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
        return jsonify({"error": "আপনার দেওয়া কান্ট্রিটি খুঁজে পাওয়া যায়নি।", "suggestion": None}), 404
    if "suggestion" in country_info:
        return jsonify({"error": "আপনার দেওয়া কান্ট্রিটি খুঁজে পাওয়া যায়নি।", "suggestion": f"আপনি কি {country_info['suggestion']} খুঁজছেন?"}), 404
    url_part = country_info["url_part"]
    full_url = f"https://outputter.io/full-identity/{url_part}/"
    scraped_data = scrape_data(full_url)
    if "error" in scraped_data:
        return jsonify(scraped_data), 500
    else:
        return jsonify(scraped_data), 200

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """
    সমস্ত সমর্থিত দেশের তালিকা প্রদান করে।
    """
    return jsonify(countries_data)

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    API স্বাস্থ্য অবস্থা পরীক্ষা করে।
    """
    return jsonify({"status": "healthy", "message": "API is running smoothly."})

@app.route('/', methods=['GET'])
def home():
    """
    API ডকুমেন্টেশন এবং টেস্টিং ইন্টারফেস প্রদান করে।
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scraper API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            h1, h2 { color: #333; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .container { max-width: 800px; margin: auto; }
            form { margin-bottom: 20px; }
            input[type="text"] { width: 70%; padding: 8px; }
            button { padding: 8px 12px; cursor: pointer; }
            .response { background-color: #e9e9e9; padding: 15px; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Identity Scraper API</h1>
            <p>Welcome to the Identity Scraper API. You can use this API to get identity data for supported countries.</p>
            
            <hr>

            <h2>1. API Endpoint: `GET /api`</h2>
            <p>This endpoint scrapes identity data for a specific country.</p>
            <h3>Usage:</h3>
            <p><code>/api?country=&lt;country_code_or_name&gt;</code></p>
            
            <h3>Example:</h3>
            <p>To get data for Bangladesh, you can use either:</p>
            <ul>
                <li><a href="/api?country=bd">/api?country=bd</a></li>
                <li><a href="/api?country=bangladesh">/api?country=bangladesh</a></li>
            </ul>

            <h3>Live Test:</h3>
            <form id="apiForm">
                <label for="countryInput">Enter Country Code or Name:</label>
                <input type="text" id="countryInput" name="country" placeholder="e.g., bd or bangladesh" required>
                <button type="submit">Scrape Data</button>
            </form>
            <div class="response">
                <strong>Response:</strong>
                <pre id="apiResponse">JSON response will appear here...</pre>
            </div>

            <hr>

            <h2>2. API Endpoint: `GET /api/countries`</h2>
            <p>Get a list of all supported countries and their codes.</p>
            <h3>Usage:</h3>
            <p><code>/api/countries</code></p>
            <p><a href="/api/countries">Test this endpoint</a></p>

            <hr>
            
            <h2>3. API Endpoint: `GET /api/health`</h2>
            <p>Check the health status of the API.</p>
            <h3>Usage:</h3>
            <p><code>/api/health</code></p>
            <p><a href="/api/health">Test this endpoint</a></p>

            <script>
                document.getElementById('apiForm').addEventListener('submit', function(event) {
                    event.preventDefault();
                    const country = document.getElementById('countryInput').value;
                    const url = `/api?country=${country}`;
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('apiResponse').textContent = JSON.stringify(data, null, 2);
                        })
                        .catch(error => {
                            document.getElementById('apiResponse').textContent = `Error: ${error}`;
                        });
                });
            </script>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
