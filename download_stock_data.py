import csv
import requests
import time

API_KEY = ""
SYMBOL_LIST = ["NSE:ABCAPITAL", "NSE:ASIANPAINT", "NSE:AUROPHARMA", "NSE:COLPAL", "NSE:DIVISLAB", "NSE:DMART",
               "NSE:GRASIM", "NSE:GREENPANEL", "NSE:GREENPLY", "NSE:HATSUN", "NSE:HAVELLS", "NSE:HDFCBANK",
               "NSE:HDFCLIFE", "NSE:IDFCFIRSTB", "NSE:ITC", "NSE:LTI", "NSE:LUPIN", "NSE:MARICO", "NSE:MOTHERSUMI",
               "NSE:KANSAINER", "NSE:ORIENTREF", "NSE:PIDILITIND", "NSE:POLYCAB", "NSE:RELAXO", "NSE:SUPREMEIND",
               "NSE:VIPIND", "NSE:ICICIBANK"]

def get_url(symbol) -> str:
    return "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + \
           symbol + "&apikey=" + API_KEY + "&datatype=csv&outputsize=full"


def download_stock_data(symbol):
    response = requests.get(get_url(symbol))
    with open("_" + symbol.replace(":", "_") + '.csv', 'w') as f:
        writer = csv.writer(f)
        for line in response.iter_lines():
            writer.writerow(line.decode('utf-8').split(','))


def download_all_stock_data():
    global API_KEY
    API_KEY = input("Please enter API key for Alpha Vantage: ")
    if API_KEY == "":
        return
    for index, sym in enumerate(SYMBOL_LIST, start=1):
        print("Downloading data for " + sym + " (" + str(index) + " of " + str(len(SYMBOL_LIST)) + ")")
        download_stock_data(sym)
        if (index % 5) == 0:  # Waiting for one minute before continuing downloading as the API can have maximum of 5 requests per minute
            print("Waiting for 1 minute...")
            time.sleep(60)


download_all_stock_data()
