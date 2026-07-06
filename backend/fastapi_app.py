from backend.util.db import get_engine
from sqlalchemy import text

from fastapi import FastAPI, Query, UploadFile, File
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from backend.event_log.getEventLogs import get_event_logs, get_monitoring_status, get_dashboard_data

from ai.detect import generate_frames

app = FastAPI()

CAMERA_MAP = {
    "cctv01": 0,
    "cctv02": 1,
    "cctv03": 2,
}

app.add_middleware(SessionMiddleware, secret_key="motmachugetjyo")

# db 연결 테스트
@app.get('/db')
def db_test():
    conn = None
    try:
        conn = get_engine()
        sql = text("show tables")
        result = conn.execute(sql).fetchall()

        tables = [row[0] for row in result]

        return {
            "success": True,
            "tables": tables
        }
    except Exception as e:
        print(f"🚨 DB 연결 에러: {e}")
        return {"success": False, "message": "서버 오류가 발생했습니다."}
    finally:
        if conn:
            conn.close()


# -----------------------------
# monitoring
# -----------------------------
@app.get("/api/cctv")
def cctv_list():
    return [
        {"id": "cctv01", "name": "CCTV-01"},
        {"id": "cctv02", "name": "CCTV-02"},
        {"id": "cctv03", "name": "CCTV-03"},
    ]

@app.get("/api/video-feed/{cctv_id}")
def video_feed(cctv_id: str):

    camera = CAMERA_MAP.get(cctv_id)

    if camera is None:
        return {"success": False}

    return StreamingResponse(
        generate_frames(camera),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/monitoring/status") # 모니터링 상태 (임시 더미 데이터)
def monitoring_status(cctvId: str):

    data = get_monitoring_status(cctvId)

    return data

# -----------------------------
# event log
# -----------------------------
@app.get("/api/events")
def events(
    start_date: str = None,
    end_date: str = None,
    cctv_id: str = None
):

    data = get_event_logs(start_date, end_date, cctv_id)

    return {
        "success": True,
        "data": data
    }

# -----------------------------
# dashboard
# -----------------------------
@app.get("/api/dashboard")
def dashboard_data():
    return get_dashboard_data()