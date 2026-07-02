from backend.util.db import get_engine
from sqlalchemy import text

from fastapi import FastAPI, Query, UploadFile, File
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

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