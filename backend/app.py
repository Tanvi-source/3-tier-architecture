from flask import Flask, jsonify
import mysql.connector
import os
import time
app = Flask(__name__)
def get_db_connection():
    while True:
        try:
            db = mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST", "db"),
                user=os.environ.get("MYSQL_USER", "user"),
                password=os.environ.get("MYSQL_PASSWORD", "userpass"),
                database=os.environ.get("MYSQL_DATABASE", "testdb")
            )
            return db
        except mysql.connector.Error:
            print("Waiting for database...")
            time.sleep(2)
@app.route('/')
def home():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT 'Hello from MySQL!'")
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify({"message": result[0]})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)