from flask import Flask, Response, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

BASE = "https://bldcmprod-cdn.toffeelive.com"

# 🍪 Load cookie from cookie.json
with open("cookie.json", "r") as f:
    COOKIE = json.load(f)["cookie"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/channels")
def get_channels():
    with open("static/data/channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/<path:subpath>")
def proxy(subpath):
    """Proxy the m3u8 and segment requests with cookie"""
    url = f"{BASE}/{subpath}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    print(f"[DEBUG] Fetching: {url}")

    r = requests.get(url, headers={"Cookie": COOKIE}, stream=True)
    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("content-type", "application/octet-stream"),
        status=r.status_code,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
