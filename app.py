import os
import json
import requests
from flask import Flask, Response, render_template, request, jsonify
from dotenv import load_dotenv

# Load .env locally; on Render this will be supplied via Environment Variables
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

BASE = "https://bldcmprod-cdn.toffeelive.com"
COOKIE = os.getenv('TOFFEE_COOKIE', '')

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Channel list (from static/data/channels.json)
@app.route('/channels')
def get_channels():
    with open(os.path.join(app.static_folder, 'data', 'channels.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

# Proxy only requests that start with /cdn/  (keeps other static routes untouched)
@app.route('/cdn/<path:subpath>')
def proxy_cdn(subpath):
    # Build target url
    target_url = f"{BASE}/cdn/{subpath}"
    if request.query_string:
        target_url += f"?{request.query_string.decode()}"

    # Construct headers
    headers = {
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Referer': 'https://www.toffeelive.com/',
        'Origin': 'https://www.toffeelive.com',
        'Cookie': COOKIE
    }

    app.logger.info(f"[proxy] Fetching: {target_url}")

    # Stream response
    resp = requests.get(target_url, headers=headers, stream=True, timeout=20)

    # Build response preserving content-type
    content_type = resp.headers.get('Content-Type', 'application/octet-stream')
    return Response(resp.iter_content(chunk_size=8192), status=resp.status_code, content_type=content_type)

# Optional catch-all proxy if needed (commented out)
# @app.route('/<path:subpath>')
# def proxy_all(subpath):
#     # Use only if you need all paths proxied. Be careful with static files.
#     ...

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
