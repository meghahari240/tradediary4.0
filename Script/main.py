from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "trade_diary.db"

# -------------------------------
# CREATE DATABASE & TABLE
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            day TEXT,
            symbol TEXT,
            trade_type TEXT,
            qty INTEGER,
            entry REAL,
            exit REAL,
            strategy TEXT,
            reason_entry TEXT,
            reason_exit TEXT,
            pl REAL,
            mistakes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def index():
    return render_template("trade_diary.html")

# -------------------------------
# API: GET ALL TRADES
# -------------------------------
@app.route("/api/trades", methods=["GET"])
def get_trades():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM trades ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    trades = [dict(row) for row in rows]
    return jsonify(trades)

# -------------------------------
# API: ADD NEW TRADE
# -------------------------------
@app.route("/api/trade", methods=["POST"])
def add_trade():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO trades
        (date, day, symbol, trade_type, qty, entry, exit, strategy,
         reason_entry, reason_exit, pl, mistakes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["date"], data["day"], data["symbol"], data["trade_type"],
        data["qty"], data["entry"], data["exit"], data["strategy"],
        data["reason_entry"], data["reason_exit"], data["pl"], data["mistakes"]
    ))

    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"id": new_id}), 201

# -------------------------------
# API: UPDATE EXISTING TRADE
# -------------------------------
@app.route("/api/trade/<int:trade_id>", methods=["PUT"])
def update_trade(trade_id):
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        UPDATE trades SET
            date=?, day=?, symbol=?, trade_type=?, qty=?, entry=?, exit=?,
            strategy=?, reason_entry=?, reason_exit=?, pl=?, mistakes=?
        WHERE id=?
    """, (
        data["date"], data["day"], data["symbol"], data["trade_type"],
        data["qty"], data["entry"], data["exit"], data["strategy"],
        data["reason_entry"], data["reason_exit"], data["pl"],
        data["mistakes"], trade_id
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "updated"}), 200

# -------------------------------
# API: DELETE TRADE
# -------------------------------
@app.route("/api/trade/<int:trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM trades WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"}), 200

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
