from fastapi import FastAPI, Header, HTTPException, Query
import psycopg
import os

app = FastAPI()

API_KEY = os.environ["API_KEY"]

def get_conn():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

def check_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403)

@app.post("/focus/start")
def start_focus(data: dict, x_api_key: str = Header(...)):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO focus_sessions (focus_name, device, start_time) VALUES (%s, %s, NOW())",
                (data["focus"], data.get("device"))
            )

@app.post("/focus/stop")
def stop_focus(data: dict, x_api_key: str = Header(...)):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE focus_sessions
                SET end_time = NOW()
                WHERE id = (
                    SELECT id
                    FROM focus_sessions
                    WHERE focus_name = %s
                      AND end_time IS NULL
                    ORDER BY start_time DESC
                    LIMIT 1
                )
                """,
                (data["focus"],)
            )

@app.get("/focus/current")
def current_focus(x_api_key: str = Header(...)):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT focus_name, start_time
                FROM focus_sessions
                WHERE end_time IS NULL
                ORDER BY start_time DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row is None:
                return {
                    "active": False
                }

            return {
                "active": True,
                "focus": row[0],
                "start_time": row[1]
            }

@app.get("/stats/daily")
def daily_stats(
        x_api_key: str = Header(...),
        day_offset: int = 0,
    ):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    DATE(start_time) AS day,
                    focus_name,
                    COUNT(*) AS activations,
                    SUM(EXTRACT(EPOCH FROM COALESCE(end_time, NOW()) - start_time)/3600) AS duration_hours
                FROM focus_sessions
                WHERE start_time >= date_trunc('day', NOW()) + (%s * INTERVAL '1 day')
                AND start_time <  date_trunc('day', NOW()) + ((%s + 1) * INTERVAL '1 day')
                GROUP BY day, focus_name
                ORDER BY day, focus_name
            """, (day_offset, day_offset))
            rows = cur.fetchall()
            return [
                {"day": r[0], "focus": r[1], "hours": float(r[3]), "activations": r[2]} for r in rows
            ]

@app.get("/stats/weekly")
def weekly_stats(
        x_api_key: str = Header(...),
        week_offset: int = 0,
):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    DATE(start_time) AS day,
                    focus_name,
                    COUNT(*) AS activations,
                    SUM(EXTRACT(EPOCH FROM COALESCE(end_time, NOW()) - start_time)/3600) AS duration_hours
                FROM focus_sessions
                WHERE start_time >= date_trunc('week', NOW()) + (%s * INTERVAL '1 week')
                AND start_time <  date_trunc('week', NOW()) + ((%s + 1) * INTERVAL '1 week')
                GROUP BY day, focus_name
                ORDER BY day, focus_name
            """, (week_offset, week_offset))
            rows = cur.fetchall()
            return [
                {"week_start": r[0], "focus": r[1], "hours": float(r[3]), "activations": r[2]} for r in rows
            ]

@app.get("/stats/monthly")
def monthly_stats(x_api_key: str = Header(...)):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    DATE_TRUNC('month', start_time)::date AS month_start,
                    focus_name,
                    COUNT(*) AS activations,
                    SUM(EXTRACT(EPOCH FROM COALESCE(end_time, NOW()) - start_time)/3600) AS duration_hours
                FROM focus_sessions
                GROUP BY month_start, focus_name
                ORDER BY month_start, focus_name
            """)
            rows = cur.fetchall()
            return [
                {"month_start": r[0], "focus": r[1], "hours": float(r[2]), "activations": r[2]} for r in rows
            ]

@app.get("/stats/overall")
def overall_stats(x_api_key: str = Header(...)):
    check_key(x_api_key)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    focus_name,
                    MIN(start_time) AS first_activation,
                    COUNT(*) AS activations,
                    SUM(EXTRACT(EPOCH FROM COALESCE(end_time, NOW()) - start_time)/3600) AS duration_hours
                FROM focus_sessions
                GROUP BY focus_name
                ORDER BY focus_name;
            """)
            rows = cur.fetchall()
            return [
                {
                    "focus": r[0],
                    "first_activation": r[1].isoformat(),
                    "activations": r[2],
                    "hours": float(r[3])
                } for r in rows
            ]

