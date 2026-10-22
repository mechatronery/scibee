import time
import sqlite3
import csv
import os
import threading
from datetime import datetime, timedelta, timezone

from flask import Flask, request, send_from_directory, send_file, jsonify

# =========================================================
# CONFIGURATION
# =========================================================
app = Flask(__name__, static_folder="www", static_url_path="")

PREFIX = "MCI"
CSV_DIR = "data"

SQLITE_PATH = "today.db"

STATE_KEY = "active_day"

os.makedirs(CSV_DIR, exist_ok=True)

rollover_lock = threading.Lock()


# =========================================================
# TIME
# =========================================================
def utc_today():
    return datetime.now(timezone.utc).date()


def day_str(d):
    return d.isoformat()


# =========================================================
# SQLITE
# =========================================================
def get_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meadowData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            epoch INTEGER NOT NULL,
            type TEXT NOT NULL,
            area TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    today = day_str(utc_today())

    cur.execute("""
        INSERT OR IGNORE INTO meta(key, value)
        VALUES (?, ?)
    """, (STATE_KEY, today))

    conn.commit()
    conn.close()


def get_active_day(conn):
    row = conn.execute("""
        SELECT value FROM meta WHERE key = ?
    """, (STATE_KEY,)).fetchone()

    return row["value"] if row else None


def set_active_day(conn, day):
    conn.execute("""
        UPDATE meta SET value = ? WHERE key = ?
    """, (day, STATE_KEY))


def insert_today(epoch, meadow_type, area, lat, lng):
    conn = get_conn()
    conn.execute("""
        INSERT INTO meadowData (epoch, type, area, lat, lng)
        VALUES (?, ?, ?, ?, ?)
    """, (epoch, meadow_type, area, lat, lng))
    conn.commit()
    conn.close()


def fetch_today():
    conn = get_conn()
    rows = conn.execute("""
        SELECT epoch, type, area, lat, lng
        FROM meadowData
    """).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def clear_today(conn):
    conn.execute("DELETE FROM meadowData")


# =========================================================
# CSV
# =========================================================
def csv_path(day):
    return os.path.join(CSV_DIR, f"{PREFIX}_{day.replace('-', '_')}.csv")


def write_csv(day, rows):
    if not rows:
        return

    path = csv_path(day)

    if os.path.exists(path):
        return

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Epoch_time_ms", "Type", "Area", "Latitude", "Longitude"])

        for r in rows:
            writer.writerow([
                r["epoch"],
                r["type"],
                r["area"],
                r["lat"],
                r["lng"]
            ])


def fetch_day(day):
    path = csv_path(day)

    if not os.path.exists(path):
        return []

    data = []

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data.append({
                "epoch": int(row.get("Epoch_time_ms", 0)),
                "type": row.get("Type"),
                "area": row.get("Area"),
                "lat": float(row["Latitude"]) if row.get("Latitude") else None,
                "lng": float(row["Longitude"]) if row.get("Longitude") else None,
            })

    return data


# =========================================================
# ROLLOVER
# =========================================================
def rollover_if_needed():
    today = day_str(utc_today())

    with rollover_lock:
        conn = get_conn()

        try:
            conn.execute("BEGIN IMMEDIATE")

            active_day = get_active_day(conn)

            if active_day == today:
                conn.commit()
                return

            rows = conn.execute("""
                SELECT id, epoch, type, area, lat, lng
                FROM meadowData
            """).fetchall()

            rows = [dict(r) for r in rows]

            write_csv(active_day, rows)

            clear_today(conn)
            set_active_day(conn, today)

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise

        finally:
            conn.close()


# =========================================================
# N-DAY VIEW
# =========================================================
def fetch_last_N_days(N):
    today = utc_today()
    result = []

    for i in range(N):
        d = today - timedelta(days=i)
        d_str = day_str(d)

        if i == 0:
            data = fetch_today()
        else:
            data = fetch_day(d_str)

        result.append({
            "day": d_str,
            "data": data
        })

    return result


# =========================================================
# HOOK
# =========================================================
@app.before_request
def before_request():
    rollover_if_needed()


# =========================================================
# JSON
# =========================================================
def json_ok(data=None):
    payload = {
        "status": "ok"
    }

    if isinstance(data, dict):
        payload.update(data)
    else:
        payload["data"] = data

    return jsonify(payload), 200


def json_error(msg, code=400):
    return jsonify({
        "status": "error",
        "message": str(msg)
    }), code


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def home():
    return send_from_directory("www", "index.html")


@app.route("/getFileList", methods=["GET"])
def get_file_list():
    try:
        files = [
            f for f in os.listdir(CSV_DIR)
            if f.endswith(".csv")
            and f.startswith(PREFIX)
            and os.path.isfile(os.path.join(CSV_DIR, f))
        ]

        return json_ok(files)

    except Exception as e:
        return json_error(str(e))


def safe_file_path(name):
    name = os.path.basename(name)

    if not name.endswith(".csv"):
        raise ValueError("invalid file type")

    path = os.path.join(CSV_DIR, name)

    if not os.path.realpath(path).startswith(os.path.realpath(CSV_DIR)):
        raise ValueError("invalid path")

    return path


@app.route("/getFile", methods=["GET"])
def get_file():
    try:
        file_name = request.args.get("file_name")
        if not file_name:
            return json_error("missing file_name")

        path = safe_file_path(file_name)

        if not os.path.exists(path):
            return json_error("file not found")

        return send_file(
            path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=os.path.basename(path)
        )

    except Exception as e:
        return json_error(str(e))


@app.route("/addMeadowData", methods=["POST"])
def addMeadowData():
    data = request.get_json(force=True)

    try:
        meadow_type = data["type"]
        area = data["area"]
        lat = float(data["lat"])
        lng = float(data["lng"])

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return {"error": "invalid coordinates"}, 400

    except (KeyError, TypeError, ValueError):
        return {"error": "invalid payload"}, 400

    insert_today(
        epoch=int(time.time() * 1000),
        meadow_type=meadow_type,
        area=area,
        lat=lat,
        lng=lng
    )

    return {"status": "ok"}


@app.route("/getMeadowData", methods=["GET"])
def getMeadowData():
    return {"status": "ok", "data": fetch_last_N_days(14)}


@app.route("/today", methods=["GET"])
def today():
    return {"status": "ok", "data": fetch_today()}


@app.route("/day/<d>", methods=["GET"])
def day(d):
    if d == day_str(utc_today()):
        return {"status": "ok", "data": fetch_today()}

    return {"status": "ok", "data": fetch_day(d)}


# =========================================================
# MAIN
# =========================================================
def main():
    init_db()
    app.run(host="0.0.0.0", port=8080, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
