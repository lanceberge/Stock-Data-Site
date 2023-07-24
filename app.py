from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/key_statistics')
def key_statistics():
    ticker = request.args.get('ticker')

    query = f"SELECT * FROM test WHERE id={ticker}"
    # TODO if data is too old or nonexistent, call API and replace data

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)


@app.route('/balance_sheet')
def balance_sheet():
    pass


@app.route('/earnings')
def earnings():
    pass


@app.route('/cash_flow')
def cash_flow():
    pass


@app.route('/insider_trading')
def insider_trading():
    pass


if __name__ == '__main__':
    app.run(debug=True)
