from flask import Flask, Response, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Initial cookie
CURRENT_COOKIE = "Edge-Cache-Cookie=URLPrefix=aHR0cHM6Ly9ibGRjbXByb2QtY2RuLnRvZmZlZWxpdmUuY29t:Expires=1762061608:KeyName=prod_linear:Signature=DDuB11d3OvYte3cd5ivuqPhjPyf5OVfPugJAFHDG6nF1ZjjgwAAPbsyl7XszNtAWBxPyA3ARyZpP2p5lzt14AA"

BASE = "https://bldcmprod-cdn.toffeelive.com"

# -------------------------------
# Public Player
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# Admin Cookie Update
# -------------------------------
@app.route("/admin/cookie", methods=["GET", "POST"])
def admin_cookie():
    global CURRENT_COOKIE
    message = ""
    if request.method == "POST":
        new_cookie = request.form.get("cookie")
        if new_cookie:
            CURRENT_COOKIE = new_cookie.strip()
            message = "Cookie updated successfully!"
    return render_template("admin/cookie_form.html", cookie_value=CURRENT_COOKIE, message=message)


# -------------------------------
# Channels JSON
# -------------------------------
@app.route("/channels")
def get_channels():
    import json
    with open("static/data/channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# -------------------------------
# Proxy route with CURRENT_COOKIE
# -------------------------------
@app.route("/<path:subpath>")
def proxy(subpath):
    url = f"{BASE}/{subpath}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    print(f"[DEBUG] Fetching URL: {url}")
    r = requests.get(url, headers={"Cookie": CURRENT_COOKIE}, stream=True)

    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("content-type", "application/octet-stream"),
        status=r.status_code,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
