from flask import Flask, Response, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

COOKIE_FILE = "static/data/cookie.json"
BASE = "https://bldcmprod-cdn.toffeelive.com"

def get_cookie():
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("TOFFEE_COOKIE", "")

def set_cookie(new_cookie):
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump({"TOFFEE_COOKIE": new_cookie}, f)

# --- Frontend ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# --- Cookie API ---
@app.route("/api/get-cookie")
def api_get_cookie():
    return jsonify({"TOFFEE_COOKIE": get_cookie()})

@app.route("/api/set-cookie", methods=["POST"])
def api_set_cookie():
    data = request.get_json()
    if "TOFFEE_COOKIE" in data:
        set_cookie(data["TOFFEE_COOKIE"])
        return jsonify({"message": "Cookie updated successfully!"})
    return jsonify({"message": "No cookie provided"}), 400

# --- Channels API ---
@app.route("/channels")
def get_channels():
    with open("static/data/channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

# --- Proxy for m3u8 & segment requests ---
@app.route("/<path:subpath>")
def proxy(subpath):
    url = f"{BASE}/{subpath}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    cookie = get_cookie()
    r = requests.get(url, headers={"Cookie": cookie}, stream=True)
    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("content-type", "application/octet-stream"),
        status=r.status_code,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
