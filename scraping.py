# Webscraping Yahoo Finance Historical Data
# Date: 10.11.2020
# Author: Roman Schulze

# import relevant libraries
from bs4 import BeautifulSoup
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import requests

# define a webscraping function that takes a yahoo finance url of historical stock data as an input
# the function returns a pandas dataframe containing seven columns
def web_scraper(yahoo_url):
    # define url
    url = yahoo_url
    # get contents of url using request
    page = requests.get(url).text
    # create a BeautifulSoup object for further processing
    soup = BeautifulSoup(page, "html.parser")
    # get the table contents using the class attribute
    bc_table = soup.find(class_="W(100%) M(0)")
    # get the body of the table
    body = bc_table.find("tbody")
    # filter table rows
    table_rows = body.find_all("tr")
    # derive the number of columns by accessing the length of the first row
    len_of_each_row = len(table_rows[0])
    # create a list with column names
    columns = ["Date", "Open", "Max",
               "Min", "Close", "Adj Close", "Volume"]

    # create an empty dictionary to store the results
    dic = {}
    # empty list to store results
    container = []
    # take each column one after the other
    for c in range(len(columns)):
        # loop over the rows of table which we extracted from the body
        for k in range(len(table_rows)):
            try:
                # try to extract the corresponding column value for each row
                container.append(table_rows[k].find_all("td")[c].text)
            except:
                # if there is no value fill with missing
                container.append(np.nan)
        # after walking the body from top to bottom add values to it´s column key
        dic[columns[c]] = container
        # clear list for the next round
        container = []

    # convert the dictionary to a dataframe
    df = pd.DataFrame(dic)
    # return the dataframe
    return(df)


# For further adjustments of the dataframe the follwing function might be helpful
def clean_data(df):
    # drop row if it contains more than 3 na´s
    df.dropna(thresh=4, axis=0, inplace=True)
    # Adjust strings for further processing of the data
    for col in df.columns:
        if col == "Date":
            df[col] = df[col].str.replace(",", "")
        if col != "Date":
            df[col] = df[col].str.replace(",", "")
            df.loc[df[col].str.contains("-"), col] = np.nan
    # convert object dtypes to integers
    for col in df.columns:
        if col != "Date":
            df[col] = df[col].astype("float")
    # convert Date into datetime object
    df["Date"] = [datetime.strptime(date, "%b %d %Y") for date in df["Date"]]
    # set date column as index
    df.set_index("Date", inplace=True)
    # return final dataframe
    return df

# plot stock data
# input df is the dataframe derived from calling the webscraper function
# the input variable vars has to be an iterable, e.g. a list
# Add a title based on input data
def plot_data(df, vars, title):
    # plot each variable in the list of vars
    for var in vars:
        df[var].plot(alpha=0.6)
    # Add a title
    plt.title(title)
    # Add ylabel
    plt.ylabel("US-Dollar")
    # Add a legend
    plt.legend()
    # Update x-axis
    ax = plt.gca()
    # change label frequency of x-axis to monthly
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # Format date
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    # Rotate
    plt.gcf().autofmt_xdate()
    # plot data
    plt.show()


# Check webscraper using historical Apple data
aapl = web_scraper("https://finance.yahoo.com/quote/AAPL/history?p=AAPL")
# clean data
aapl = clean_data(aapl)
# print first five rows
print(aapl.head())
# print dtypes of data
print(aapl.dtypes)
# plot data
plot_data(aapl, ["Open", "Close"], "Price Development of Apple Stock")
