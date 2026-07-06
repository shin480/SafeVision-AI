from backend.util.db import get_engine
from sqlalchemy import text


def get_event_logs(start_date=None, end_date=None, cctv_id=None):

    conn = None

    try:
        conn = get_engine()

        sql = """
            SELECT
                e.event_id AS id,
                DATE_FORMAT(e.detected_at, '%Y-%m-%d %H:%i:%s') AS time,
                c.cctv_name AS cctv,
                e.violation_type AS type,
                e.risk_level AS risk,
                e.risk_score AS score,
                e.status AS status,
                '' AS memo,
                e.capture_path
            FROM event_log e
            JOIN cctv c
                ON e.cctv_id = c.cctv_id
            WHERE 1=1
        """

        params = {}

        if start_date:
            sql += " AND DATE(e.detected_at) >= :start_date"
            params["start_date"] = start_date

        if end_date:
            sql += " AND DATE(e.detected_at) <= :end_date"
            params["end_date"] = end_date

        if cctv_id and cctv_id != "all":
            sql += " AND e.cctv_id = :cctv_id"
            params["cctv_id"] = cctv_id

        sql += " ORDER BY e.detected_at DESC"

        result = conn.execute(text(sql), params).mappings().all()

        return [dict(row) for row in result]

    except Exception as e:
        print("이벤트 조회 오류 :", e)
        return []

    finally:
        if conn:
            conn.close()