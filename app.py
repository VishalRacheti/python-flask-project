from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)

# Database configuration from environment variables (with defaults)
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None

@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/write', methods=['POST'])
def write_data():
    if not request.is_json:
        return jsonify(error="Request must be JSON"), 400

    data = request.json
    name = data.get('name')
    age = data.get('age')

    if not name or age is None:
        return jsonify(error="Missing 'name' or 'age' in request"), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify(error="Database connection failed"), 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", (name, age))
        connection.commit()
    except pymysql.MySQLError as e:
        return jsonify(error=str(e)), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(message="Data written successfully"), 201

@app.route('/read', methods=['GET'])
def read_data():
    connection = get_db_connection()
    if connection is None:
        return jsonify(error="Database connection failed"), 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    except pymysql.MySQLError as e:
        return jsonify(error=str(e)), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify(users)

@app.route('/')
def home():
    return 'Flask is working through nginx!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
