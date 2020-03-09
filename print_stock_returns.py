import matplotlib.pyplot as plt
from datetime import datetime
import mplcursors
import pandas as pd
from matplotlib.axes import Axes
from pandas import DataFrame
from stock_data import STOCK_DATA
from scipy import optimize
import numpy as np
import os.path
from os import path

# Name of the share that you want of generate chart
GENERATE_CHART_FOR: str = "Greenply Industries"

XIRR_Y_AXIS_LIMITS = [-50, 50]
XIRR_Y_AXIS_INTERVAL = 25
DATE_FORMAT: str = "%Y-%m-%d"


def get_axis_ticks(limits, interval):
    return np.arange(limits[0], limits[1], interval)


# Read the CSV file and
def read_csv_file(symbol: str) -> DataFrame:
    file_name: str = "_" + symbol.replace(":", "_") + ".csv"
    if not path.exists(file_name):
        return None
    # Read CSV file
    stock_data: DataFrame = pd.read_csv(file_name)
    # Remove any rows with zero values as that might be incorrect
    stock_data = stock_data[stock_data["close"] != 0]
    return stock_data


def generate_chart():
    # Get the stock buy data JSON and sort it in ascending order according to date
    stock_buy_data = STOCK_DATA[GENERATE_CHART_FOR]
    stock_buy_data = sorted(
        stock_buy_data,
        key=lambda x: datetime.strptime(x['date'], DATE_FORMAT)
    )

    # Create data frame that will be used to plot the charts
    stock_df: DataFrame = pd.DataFrame(columns=["timestamp", "principal_value", "investment_value", "xirr"])

    cash_flow = []

    # Loop through the buy data
    for index, sbd in enumerate(stock_buy_data, start=1):
        # Read data from CSV file
        stock_data: DataFrame = read_csv_file(sbd["symbol"])
        if stock_data is None:
            print("ERROR: Unable to find downloaded stock data for '" + sbd["symbol"] +
                  "'. Please run 'download_stock_data.py'.")
            return
        # Filter data to show values from first buy date
        stock_data = stock_data[stock_data["timestamp"] >= sbd["date"]]
        # Add quantity data
        stock_data["quantity"] = sbd["quantity"]
        # Calculate principal value
        stock_data["principal_value"] = sbd["price"] * sbd["quantity"]
        # Calculate investment value
        stock_data["investment_value"] = stock_data["close"] * stock_data["quantity"]
        # Create cash flow array for calculating XIRR
        if sbd["price"] != 0:
            cash_flow.append(
                [datetime.strptime(sbd['date'], DATE_FORMAT).date(), (sbd["price"] * sbd["quantity"] * -1)])

        # Set principal and investment value in data frame
        stock_df: DataFrame
        if index == 1:
            stock_df["timestamp"] = pd.to_datetime(stock_data['timestamp'], format=DATE_FORMAT)
            stock_df["principal_value"] = stock_data["principal_value"]
            stock_df["investment_value"] = stock_data["investment_value"]
            stock_df.loc[stock_df['timestamp'] >= sbd["date"], "xirr"] = stock_df.apply(
                lambda row: calculate_xirr(cash_flow, row["timestamp"], row['investment_value']), axis="columns")
        else:
            condition = stock_df['timestamp'] >= sbd["date"]
            stock_df.loc[condition, "principal_value"] = stock_df['principal_value'] + stock_data['principal_value']
            stock_df.loc[condition, "investment_value"] = stock_df['investment_value'] + stock_data['investment_value']
            stock_df.loc[condition, "xirr"] = stock_df.apply(
                lambda row: calculate_xirr(cash_flow, row["timestamp"], row['investment_value']), axis="columns")

    # Sort the data frame values v=by timestamp in ascending order
    stock_df = stock_df.sort_values(by=['timestamp'], ascending=True)

    # Plot the graph
    ax1: Axes
    ax2: Axes
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex="all", squeeze=True, gridspec_kw={"height_ratios": [2, 1]})
    plt.subplots_adjust(hspace=0.05)
    stock_df.plot(kind='line', x="timestamp", y="principal_value", ax=ax1, color="red")
    stock_df.plot(kind='line', x="timestamp", y="investment_value", ax=ax1, color="blue", grid=True)
    stock_df.plot(kind='line', x="timestamp", y="xirr", ax=ax2, color="green", grid=True, ylim=XIRR_Y_AXIS_LIMITS)
    ax1.set_title(GENERATE_CHART_FOR)
    ax2.set_yticks(get_axis_ticks(XIRR_Y_AXIS_LIMITS, XIRR_Y_AXIS_INTERVAL))
    ax2.axhline(y=0, color="black", linewidth=1.5, linestyle="dotted")
    plt.grid(b=True, which="minor", axis="y")
    mplcursors.cursor(hover=True)
    plt.show()


def calculate_xirr(cash_flow, date_value, investment_value):
    # Create new copy of cash flow so that reference to passed argument is removed
    temp_cash_flow = cash_flow[:]
    temp_cash_flow.append([date_value.date(), investment_value])
    return xirr(temp_cash_flow)


# Function to calculate XIRR - https://github.com/peliot/XIRR-and-XNPV/blob/master/financial.py
def xnpv(rate, cashflows):
    chron_order = sorted(cashflows, key=lambda x: x[0])
    t0 = chron_order[0][0]
    return sum([cf / (1 + rate) ** ((t - t0).days / 365.0) for (t, cf) in chron_order])


def xirr(cashflows, guess=0.1):
    xirr_value: float
    try:
        xirr_value = optimize.newton(lambda r: xnpv(r, cashflows), guess)
    except:
        xirr_value = 0
    if isinstance(xirr_value, complex):
        xirr_value = 0
    return round(xirr_value * 100, 2)
    # return xirr_value * 100


generate_chart()
