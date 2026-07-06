from backend.util.db import get_engine
from sqlalchemy import text
import cv2

CAMERA_MAP = {
            "cctv01": 0,
            "cctv02": 1,
            "cctv03": 2,
        }

# 이벤트 로그
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

# 실시간 모니터링
def get_monitoring_status(cctvId=None):
    conn = None

    try:
        conn = get_engine()

        # 1. 해당 CCTV의 최신 감지 로그
        latest_detection_sql = text("""
            SELECT
                worker_count,
                helmet_count,
                no_helmet_count,
                vest_count,
                no_vest_count,
                ppe_wear_rate,
                detected_at
            FROM detection_log
            WHERE cctv_id = :cctv_id
            ORDER BY detected_at DESC
            LIMIT 1
        """)

        detection = conn.execute(
            latest_detection_sql,
            {"cctv_id": cctvId}
        ).mappings().first()

        # 2. 해당 CCTV의 최신 이벤트
        latest_event_sql = text("""
            SELECT
                risk_score,
                risk_level,
                violation_type,
                detected_at
            FROM event_log
            WHERE cctv_id = :cctv_id
            ORDER BY detected_at DESC
            LIMIT 1
        """)

        event = conn.execute(
            latest_event_sql,
            {"cctv_id": cctvId}
        ).mappings().first()

        # 3. 오늘 위반 현황 집계
        violation_count_sql = text("""
            SELECT
                SUM(CASE WHEN violation_type = '안전모 미착용' THEN 1 ELSE 0 END) AS helmet_violation,
                SUM(CASE WHEN violation_type = '안전조끼 미착용' THEN 1 ELSE 0 END) AS vest_violation,
                SUM(CASE WHEN violation_type = '위험구역 침입' THEN 1 ELSE 0 END) AS zone_violation
            FROM event_log
            WHERE cctv_id = :cctv_id
              AND DATE(detected_at) = CURDATE()
        """)

        violations = conn.execute(
            violation_count_sql,
            {"cctv_id": cctvId}
        ).mappings().first()

        risk_level = event["risk_level"] if event else "SAFE"
        risk_score = event["risk_score"] if event else 0

        risk_text_map = {
            "SAFE": "안전",
            "WARNING": "주의",
            "DANGER": "위험",
            "CRITICAL": "심각"
        }
        print(cctvId, risk_level, risk_text_map)

        return {
            "cctvId": cctvId,
            "riskLevel": risk_level,
            "riskText": risk_text_map.get(risk_level, "-"),
            "riskScore": risk_score,

            "workerCount": detection["worker_count"] if detection else 0,
            "helmetCount": detection["helmet_count"] if detection else 0,
            "noHelmetCount": detection["no_helmet_count"] if detection else 0,
            "vestCount": detection["vest_count"] if detection else 0,
            "noVestCount": detection["no_vest_count"] if detection else 0,
            "ppeRate": float(detection["ppe_wear_rate"]) if detection and detection["ppe_wear_rate"] is not None else 0,

            "violations": {
                "helmet": int(violations["helmet_violation"] or 0),
                "vest": int(violations["vest_violation"] or 0),
                "zone": int(violations["zone_violation"] or 0)
            },

            "lastDetected": str(detection["detected_at"]) if detection else "-"
        }

    except Exception as e:
        print("모니터링 상태 조회 오류:", e)
        return {
            "cctvId": cctvId,
            "riskLevel": "SAFE",
            "riskText": "조회 실패",
            "riskScore": 0,
            "violations": {
                "helmet": 0,
                "vest": 0,
                "zone": 0
            }
        }

    finally:
        if conn:
            conn.close()

# 대시보드
def get_dashboard_data():
    conn = None

    try:
        conn = get_engine()

        # 오늘 전체 경고/위반 수
        today_warning_sql = text("""
            SELECT COUNT(*) AS count
            FROM event_log
            WHERE DATE(detected_at) = CURDATE()
        """)

        today_warning = conn.execute(today_warning_sql).mappings().first()
        today_warning_count = today_warning["count"] if today_warning else 0

        # 오늘 평균 PPE 착용률
        ppe_sql = text("""
            SELECT AVG(ppe_wear_rate) AS avg_ppe_rate
            FROM detection_log
            WHERE DATE(detected_at) = CURDATE()
        """)

        ppe_result = conn.execute(ppe_sql).mappings().first()
        ppe_rate = ppe_result["avg_ppe_rate"] if ppe_result else None
        ppe_rate = round(float(ppe_rate), 1) if ppe_rate is not None else 0

        # CCTV 연결 상태
        total_cctv = len(CAMERA_MAP)
        connected_cctv = 0

        for camera_index in CAMERA_MAP.values():
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

            if cap.isOpened():
                connected_cctv += 1

            cap.release()

        # 오늘 최고 위험도
        overall_sql = text("""
            SELECT risk_level, risk_score
            FROM event_log
            WHERE DATE(detected_at) = CURDATE()
            ORDER BY risk_score DESC
            LIMIT 1
        """)

        overall = conn.execute(overall_sql).mappings().first()

        if overall:
            overall_status = overall["risk_level"]
        else:
            overall_status = "SAFE"

        status_text_map = {
            "SAFE": "안전 상태입니다.",
            "WARNING": "주의가 필요합니다.",
            "DANGER": "위험 상황이 감지되었습니다.",
            "CRITICAL": "심각한 위험 상황입니다."
        }

        # 최근 이벤트 5개
        recent_sql = text("""
            SELECT
                DATE_FORMAT(e.detected_at, '%H:%i:%s') AS time,
                c.cctv_name AS cctv,
                e.violation_type AS violation,
                e.risk_level AS riskLevel,
                e.status AS status
            FROM event_log e
            JOIN cctv c
                ON e.cctv_id = c.cctv_id
            ORDER BY e.detected_at DESC
            LIMIT 5
        """)

        recent_events = conn.execute(recent_sql).mappings().all()

        return {
            "overallStatus": {
                "status": overall_status,
                "text": status_text_map.get(overall_status, "-")
            },
            "todayWarning": {
                "count": today_warning_count,
                "change": None,
                "changeText": None
            },
            "ppeRate": {
                "rate": ppe_rate,
                "change": None,
                "changeText": None
            },
            "cctv": {
                "connected": connected_cctv,
                "total": total_cctv,
                "text": "정상 연결" if connected_cctv == total_cctv else "일부 연결 안 됨"
            },
            "recentEvents": [dict(row) for row in recent_events]
        }

    except Exception as e:
        print("대시보드 조회 오류:", e)

        return {
            "overallStatus": {
                "status": "SAFE",
                "text": "조회 실패"
            },
            "todayWarning": {
                "count": 0,
                "change": None,
                "changeText": None
            },
            "ppeRate": {
                "rate": 0,
                "change": None,
                "changeText": None
            },
            "cctv": {
                "connected": 0,
                "total": 0,
                "text": "조회 실패"
            },
            "recentEvents": []
        }

    finally:
        if conn:
            conn.close()