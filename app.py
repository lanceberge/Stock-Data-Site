from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/key_statistics')
def key_statistics():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM test')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# TODO create similar routes for other tabs

if __name__ == '__main__':
    app.run(debug=True)
