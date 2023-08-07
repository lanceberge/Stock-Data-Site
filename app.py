from flask import Flask, render_template, request
import sqlite3
from urllib.request import urlopen
import certifi
import json

app = Flask(__name__)
base_url = "https://financialmodelingprep.com/api/v3/"
api_key = None
with open(".api_key", "r") as f:
    api_key = f.read()


def retrieve_from_api(metric, ticker):
    url = f"{base_url}{metric}/{ticker}?apikey={api_key}"

    # TODO cafile is deprecated
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")

    # TODO error handling for empty data or erroneous response
    data_dict = json.loads(data)[0]
    return data_dict


@app.route("/key_statistics")
def key_statistics():
    ticker = request.args.get("ticker")

    # query = f"SELECT * FROM test WHERE id={ticker}"
    # TODO if data is too old or nonexistent, call API and replace data

    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()
    # cursor.execute(query)
    # data = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # if len(data) == 0:
    #     return jsonify([])

    # return jsonify(data[0])

    # join the price dictionary and key statistics dictionary
    data_dict = retrieve_from_api("quote-short", ticker) | retrieve_from_api(
        "key-metrics", ticker
    )

    # TODO profit margins, EPS, FCF
    name_to_api_name = {
        "Price": "price",
        "Market Cap": "marketCap",
        "EV/EBITDA": "enterpriseValueOverEBITDA",
        "P/E": "peRatio",
        "P/B": "pbRatio",
        "P/S": "priceToSalesRatio",
        "ROIC": "roic",
    }

    data = {k: data_dict[name_to_api_name[k]] for k in name_to_api_name.keys()}
    return json.dumps(data)


@app.route("/balance_sheet")
def balance_sheet():
    return json.dumps([])


@app.route("/earnings")
def earnings():
    return json.dumps([])


@app.route("/cash_flow")
def cash_flow():
    return json.dumps([])


@app.route("/insider_trading")
def insider_trading():
    return json.dumps([])


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
