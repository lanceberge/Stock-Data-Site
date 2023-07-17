from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Database connection and API endpoint remain the same as mentioned in the previous Flask example

@app.route('/')
def display_data():
    con = sqlite3.connect("database.db")
    cursor = con.cursor()
    query = 'SELECT * FROM database'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    # Pass the data to the HTML template for rendering
    return render_template("index.html", key_statistics=data)

if __name__ == '__main__':
    app.run()
