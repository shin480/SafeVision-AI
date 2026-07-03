from flask import Flask, render_template, jsonify
import os
import requests
from flask import Response
from flask import request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FASTAPI_URL = "http://127.0.0.1:8000"

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")


#----------------
# 모니터링
#----------------
@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


@app.route("/api/cctv")
def cctv_list():
    response = requests.get(f"{FASTAPI_URL}/api/cctv")
    return jsonify(response.json())

@app.route("/api/video-feed/<cctv_id>")
def video_feed(cctv_id):
    response = requests.get(
        f"{FASTAPI_URL}/api/video-feed/{cctv_id}",
        stream=True
    )

    return Response(
        response.iter_content(chunk_size=1024),
        content_type=response.headers["Content-Type"]
    )

@app.route("/api/monitoring/status")
def monitoring_status():
    cctv_id = request.args.get("cctvId")
    response = requests.get(
        f"{FASTAPI_URL}/api/monitoring/status",
        params={"cctvId": cctv_id}
    )
    return jsonify(response.json())

@app.route("/event-log")
def event_log():
    return render_template("event-log.html")

@app.route("/statistics")
def cctv_manage():
    return render_template("statistics.html")

@app.route("/sidebar")
def sidebar():
    return render_template("sidebar.html")

# db 연결 테스트 
@app.route("/db")
def db():
    response = requests.get(f"{FASTAPI_URL}/db")
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True, port=5000)