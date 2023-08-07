from flask import Flask, render_template, request
import sqlite3
from urllib.request import urlopen
import certifi
import json
from util.number_formatting import millify, percentify, two_decimals

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
    # TODO all key_metrics are TTM
    key_metrics = retrieve_from_api("key-metrics", ticker)
    key_metrics.pop("marketCap")
    data_dict = (
        retrieve_from_api("quote-short", ticker)
        | key_metrics
        | retrieve_from_api("market-capitalization", ticker)
    )

    # TODO profit margins, EPS, FCF
    data = {}
    data["Price"]      = millify(data_dict["price"])
    data["Market Cap"] = millify(data_dict["marketCap"])
    data["EV/EBITDA"]  = millify(data_dict["enterpriseValueOverEBITDA"])
    data["P/E"]        = two_decimals(data_dict["peRatio"])
    data["P/B"]        = two_decimals(data_dict["pbRatio"])
    data["P/S"]        = two_decimals(data_dict["priceToSalesRatio"])
    data["ROIC"]       = percentify(data_dict["roic"])

    return json.dumps(data)
    # TODO data into database AFTER it's been sent to the frontend


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
