from flask import Flask, render_template, request, jsonify, send_file
from scraper import scrape_url
import csv, io, json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/scrape")
def scrape():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    options = data.get("options") or {}

    if not url:
        return jsonify({"error": "Please enter a URL."}), 400

    try:
        result = scrape_url(url, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/export")
def export():
    data = request.get_json(silent=True) or {}
    rows = data.get("rows", [])
    fmt = data.get("format", "csv")

    if not isinstance(rows, list) or not rows:
        return jsonify({"error": "No data to export."}), 400

    if fmt == "json":
        payload = json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
        return send_file(io.BytesIO(payload), mimetype="application/json",
                         as_attachment=True, download_name="scraped_data.json")

    output = io.StringIO()
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)

    writer = csv.DictWriter(output, fieldnames=keys)
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8-sig")
    return send_file(io.BytesIO(payload), mimetype="text/csv",
                     as_attachment=True, download_name="scraped_data.csv")

if __name__ == "__main__":
    app.run(debug=True)
