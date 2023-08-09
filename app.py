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


def retrieve_from_api(metric, ticker, args=None):
    url = f"{base_url}{metric}/{ticker}?apikey={api_key}"

    if args:
        args = "&".join(args)
        url = f"{base_url}{metric}/{ticker}?{args}&apikey={api_key}"

    print(url)

    # TODO cafile is deprecated
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")

    # TODO error handling for empty data or erroneous response
    data_dict = json.loads(data)
    return data_dict


@app.route("/key_statistics")
def key_statistics():
    ticker = request.args.get("ticker")

    # TODO
    # Load stock price and date from the database
    # If the Price has changed by 5% or if there have been recent earnings/filings, then load data from API
    # otherwise, load everything from the database

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

    data_dict = (
        retrieve_from_api("quote-short", ticker)[0]
        | retrieve_from_api("key-metrics-ttm", ticker)[0]
        | retrieve_from_api("market-capitalization", ticker)[0]
    )

    # TODO profit margins, EPS, FCF
    data = {}
    data["Price"] = millify(data_dict["price"])
    data["Market Cap"] = millify(data_dict["marketCap"])
    data["EV/EBITDA"] = millify(data_dict["enterpriseValueOverEBITDATTM"])
    data["P/E"] = two_decimals(data_dict["peRatioTTM"])
    data["P/B"] = two_decimals(data_dict["pbRatioTTM"])
    data["P/S"] = two_decimals(data_dict["priceToSalesRatioTTM"])
    data["ROIC"] = percentify(data_dict["roicTTM"])
    data["Dividend Yield"] = percentify(data_dict["dividendYieldTTM"])
    data["Payout Ratio"] = percentify(data_dict["payoutRatioTTM"])

    return json.dumps(data)


@app.after_request
def after_key_statistics(response):
    # TODO data into database AFTER it's been sent to the frontend
    return response


@app.route("/balance_sheet")
def balance_sheet():
    # TODO quarterly
    ticker = request.args.get("ticker")
    balance_sheet = retrieve_from_api(
        "balance-sheet-statement", ticker, args=["limit=120"]
    )

    data = []

    first_year_cash_value = balance_sheet_data[-1]["cashAndCashEquivalents"]
    thousands_base = get_thousands_base(thousands_base)

    for balance_sheet_data in balance_sheet[::-1]:
        data_for_year = {}

        data_for_year["Date"] = "/".join(balance_sheet_data["date"].split("-")[1:])
        data_for_year["Cash and Cash Equivalents"] = millify(
            balance_sheet_data["cashAndCashEquivalents"],
            thousands_base=thousands_base,
            include_suffix=False,
        )

        data.append(data_for_year)

    return json.dumps(data)


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
