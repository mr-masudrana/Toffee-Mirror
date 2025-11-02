from flask import Flask, Response, render_template, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

# Base stream server
BASE = "https://bldcmprod-cdn.toffeelive.com"
COOKIE = os.getenv("TOFFEE_COOKIE")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/channels")
def get_channels():
    """Return channel list from static/data/channels.json"""
    with open("static/data/channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/<path:subpath>")
def proxy(subpath):
    url = f"{BASE}/{subpath}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    print(f"[DEBUG] Fetching URL: {url}")
    print(f"[DEBUG] Using Cookie: {COOKIE[:30]}...")  # শুধু শুরু অংশ দেখাব

    r = requests.get(url, headers={"Cookie": COOKIE}, stream=True)
    print(f"[DEBUG] Response Status: {r.status_code}")

    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("content-type", "application/octet-stream"),
        status=r.status_code,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
