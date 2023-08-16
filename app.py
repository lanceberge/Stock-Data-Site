from flask import Flask, render_template, request, g
import sqlite3
import requests
import json
from util.number_formatting import *

app = Flask(__name__)
base_url = "https://financialmodelingprep.com/api/v3/"
api_key = None
with open(".api_key", "r") as f:
    api_key = f.read()


# TODO error handling for empty data or erroneous response
def retrieve_from_api(metric, ticker, args=None):
    url = f"{base_url}{metric}/{ticker}?apikey={api_key}"

    if args:
        args = "&".join(args)
        url = f"{base_url}{metric}/{ticker}?{args}&apikey={api_key}"

    data = requests.get(url)
    data_dict = json.loads(data.text)
    return data_dict


# TODO transition to MySQL
def execute_query(query):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query)
    # data = cursor.fetchall()
    cursor.close()
    conn.close()

    # if len(data) == 0:
    #     return jsonify([])

    # # TODO if any of these values are empty, call API
    # return jsonify(data[0])


def add_to_database(data, database):
    # if data is 2d, ex. if it's a dict
    # insert into the respective columns

    # if it's a list of dicts, idek

    # TODO if key exists in data, update it

    columns = ", ".join(data.keys())
    values = ", ".join(data.values())
    query = f"INSERT INTO {database} ({columns}) VALUES ({values})"
    execute_query(query)


def retrieve_from_database(ticker, database):
    pass


@app.route("/key_statistics")
def key_statistics():
    ticker = request.args.get("ticker")

    # TODO if data is too old or nonexistent, call API and replace data

    # TODO Load stock price and date from the database
    # If the Price has changed by 5% or if there have been recent earnings/filings, then load data from API
    # otherwise, load everything from the database

    # TODO use update instead
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

    g.ticker = ticker
    g.data = data

    return json.dumps(data)


@app.after_request
def after_key_statistics(response):
    # TODO data into database AFTER it's been sent to the frontend
    return response


@app.route("/balance_sheet")
def balance_sheet():
    # TODO quarterly
    ticker = request.args.get("ticker")
    api_data = retrieve_from_api("balance-sheet-statement", ticker, args=["limit=120"])

    first_value = api_data[-1]["cashAndCashEquivalents"]
    thousands_base = get_thousands_base(first_value) - 1

    return_map = {}
    return_map["Base"] = thousands_base

    api_ids_to_keep = [
        "cashAndCashEquivalents",
        "shortTermInvestments",
        "netReceivables",
        "inventory",
        "otherCurrentAssets",
        "totalCurrentAssets",
        "propertyPlantEquipmentNet",
        "intangibleAssets",
        "otherNonCurrentLiabilities",
        "totalNonCurrentLiabilities",
        "longTermDebt",
        "accountPayables",
        "totalLiabilities",
    ]

    return_map["Data"] = get_data_from_api_map(
        api_data, api_ids_to_keep, thousands_base
    )
    return json.dumps(return_map)


@app.route("/income_statement")
def income_statement():
    ticker = request.args.get("ticker")
    api_data = retrieve_from_api("income-statement", ticker, args=["limit=120"])

    first_value = api_data[-1]["revenue"]
    thousands_base = get_thousands_base(first_value) - 1

    return_map = {}
    return_map["Base"] = thousands_base

    # TODO gross profit ratio
    income_statement_names = [
        "revenue",
        "costOfRevenue",
        "grossProfit",
        "operatingExpenses",
        "ebitda",
        "netIncome",
    ]

    return_map["Data"] = get_data_from_api_map(
        api_data, income_statement_names, thousands_base
    )

    earnings_names = ["eps", "epsdiluted"]

    earnings_data = get_data_from_api_map(api_data, earnings_names, include_date=False)
    return_map["Data"].extend(earnings_data)

    return json.dumps(return_map)


@app.route("/cash_flow")
def cash_flow():
    return json.dumps([])


@app.route("/earnings")
def earnings():
    return json.dumps([])


@app.route("/insider_trading")
def insider_trading():
    return json.dumps([])


def get_data_from_api_map(
    api_data, api_data_names_to_keep, thousands_base=0, include_date=True):
    format_data = lambda n: millify(
        n, thousands_base=thousands_base, include_suffix=False
    )

    return_data = []

    for api_data_column in api_data[::-1]:
        return_data_column = {}

        if include_date:
            date = api_data_column["date"].split("-")
            month, year = date[1], date[0][-2:]
            return_data_column["Date"] = month + "/" + year

        for row_name in api_data_names_to_keep:
            return_data_column[row_name] = format_data(api_data_column[row_name])

        return_data.append(return_data_column)

    return return_data


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
