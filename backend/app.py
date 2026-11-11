import os
import time

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "db"),
    user=os.getenv("DB_USER", "guest"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "guestbook"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    message VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4
"""


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def init_db(retries=30):
    """DB가 완전히 뜰 때까지 재시도한 뒤 테이블을 만든다."""
    for _ in range(retries):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(CREATE_TABLE)
            return
        except pymysql.MySQLError:
            time.sleep(2)
    raise RuntimeError("DB에 연결할 수 없습니다.")


init_db()


@app.route("/api/health")
def health():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return jsonify(status="ok")


@app.route("/api/entries", methods=["GET"])
def list_entries():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, message, created_at FROM entries ORDER BY id DESC LIMIT 50"
        )
        rows = cur.fetchall()
    for r in rows:
        r["created_at"] = str(r["created_at"])
    return jsonify(rows)


@app.route("/api/entries", methods=["POST"])
def add_entry():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    message = (data.get("message") or "").strip()
    if not name or not message:
        return jsonify(error="name과 message는 필수입니다."), 400
    if len(name) > 50 or len(message) > 500:
        return jsonify(error="입력이 너무 깁니다."), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO entries (name, message) VALUES (%s, %s)", (name, message)
        )
    return jsonify(status="created"), 201
