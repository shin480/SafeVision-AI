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
@app.route("/dashboard.html")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login.html")
def login():
    return render_template("login.html")

@app.route("/monitoring.html")
def monitoring():
    return render_template("monitoring.html")

@app.route("/event-log.html")
def event_log():
    return render_template("event-log.html")

@app.route("/statistics.html")
def cctv_manage():
    return render_template("statistics.html")

@app.route("/sidebar.html")
def sidebar():
    return render_template("sidebar.html")

# db 연결 테스트 
@app.route("/db")
def db():
    response = requests.get(f"{FASTAPI_URL}/db")
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True, port=5000)