from flask import Flask, render_template, request, g
import sqlite3
import requests
import json
from util.number_formatting import *
from util.database_management import *

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


@app.route("/key_statistics")
def key_statistics():
    ticker = request.args.get("ticker")
    
    # TODO profit margins, EPS, FCF
    price_data = retrieve_from_api("quote-short", ticker)[0]
    ttm_data = retrieve_from_api("key-metrics-ttm", ticker)[0]
    market_cap_data = retrieve_from_api("market-capitalization", ticker)[0]

    data = {}
    data["price"] = millify(price_data["price"])
    data["enterpriseValueOverEBITDATTM"] = millify(ttm_data["enterpriseValueOverEBITDATTM"], accounting_style=False)
    data["peRatioTTM"] = two_decimals(ttm_data["peRatioTTM"])
    data["pbRatioTTM"] = two_decimals(ttm_data["pbRatioTTM"])
    data["priceToSalesRatioTTM"] = two_decimals(ttm_data["priceToSalesRatioTTM"])
    data["roicTTM"] = percentify(ttm_data["roicTTM"])
    data["dividendYieldTTM"] = percentify(ttm_data["dividendYieldTTM"])
    data["payoutRatioTTM"] = percentify(ttm_data["payoutRatioTTM"])
    data["marketCap"] = millify(market_cap_data["marketCap"], include_suffix=True)

    g.ticker = ticker
    g.data = data

    return_map = {}
    return_map["Data"] = [data]
    return json.dumps(return_map)


@app.route("/balance_sheet")
def balance_sheet():
    api_ids = [
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
        "totalLiabilities"
    ]

    return_data = table_from_api_data("balance-sheet-statement", api_ids)
    return json.dumps(return_data)


@app.route("/income_statement")
def income_statement():
    api_ids = [
        "revenue",
        "costOfRevenue",
        "grossProfit",
        "grossProfitRatio",
        "operatingExpenses",
        "ebitda",
        "netIncome",
        "eps",
        "epsdiluted",
    ]

    thousands_bases = {
        "grossProfitRatio": 1,
        "eps":  1,
        "epsdiluted": 1
    }

    return_map = table_from_api_data("income-statement", api_ids, thousands_bases)

    return json.dumps(return_map)


@app.route("/cash_flow")
def cash_flow():
    api_ids = [
        "netIncome",
        "operatingCashFlow",
        "netCashUsedForInvestingActivites",
        "freeCashFlow"
    ]
    
    return_map = table_from_api_data("cash-flow-statement", api_ids)
    return json.dumps(return_map)


# TODO doc
# TODO identify the number of periods needed based on the most recent date in the db
def table_from_api_data(api_endpoint_name, api_ids, thousands_bases=None):
    g.ticker = request.args.get("ticker")
    g.period = request.args.get("period")
    api_data = retrieve_from_api(api_endpoint_name, g.ticker, args=["limit=5", f"period={g.period}"])

    return_map = {}
    return_data = []

    first_value = api_data[-1][api_ids[0]]
    default_thousands_base = get_thousands_base(first_value) - 1
    return_map["Base"] = default_thousands_base

    for api_data_column in api_data:
        return_data_column = {}

        date = api_data_column["date"].split("-")
        month, year = date[1], date[0][-2:]
        return_data_column["filingDate"] = month + "/" + year

        for api_id in api_ids:
            thousands_base = default_thousands_base
            if thousands_bases and api_id in thousands_bases:
                thousands_base = thousands_bases[api_id]

            return_data_column[api_id] = millify(api_data_column[api_id], thousands_base, include_suffix=False)

        return_data.insert(0, return_data_column)

    return_map["Data"] = return_data
    g.data = return_map["Data"]
    g.thousands_base = default_thousands_base

    return return_map


@app.after_request
def after_request(response):
    def after_balance_sheet():
        for row in g.data:
            row['base'] = g.thousands_base
            row['ticker'] = g.ticker
            row['filingPeriod'] = g.period
            # insert_into_database(row, 'BalanceSheet')

    request_to_function_map = {"/balance_sheet": after_balance_sheet}

    if request.path in request_to_function_map:
        request_to_function_map[request.path]()

    return response


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
