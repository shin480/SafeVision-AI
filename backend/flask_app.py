from flask import Flask, render_template, jsonify
import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FASTAPI_URL = "http://127.0.0.1:8000"

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/db")
def db():
    response = requests.get(f"{FASTAPI_URL}/db")
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True, port=5000)