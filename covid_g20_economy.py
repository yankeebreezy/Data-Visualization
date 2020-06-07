import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pydeck as pdk
import altair as alt
from datetime import timedelta
import datetime
import time
import pandas as pd

st.title("Economic Impact of Covid-19 on G20 Countries")

g20_indics = {
    'Argentina':'^MERV', 
    'Australia':'^AXJO', 
    'Brazil':'^BVSP', 
    'Canada':'^GSPTSE', 
    'China':'000001.SS', 
    'France':'^FCHI', 
    'Germany':'^GDAXI', 
    'India':'^BSESN', 
    'Indonesia':'^JKSE', 
    'Italy':'FTSEMIB.MI', 
    'Japan':'^N225', 
    'South Korea':'^KS11', 
    'Mexico':'^MXX', 
    'Russia':'IMOEX.ME', 
    'Saudi Arabia':'^TASI.SR', 
    'South Africa':'^JN0U.JO', 
    'Turkey':'XU100.IS', 
    'UK':'^FTSE', 
    'US':'^NYA',
    'EU':'^N100'
    }

COVID_CONFIRMED_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

g20Countries = [key for key, value in g20_indics.items()]

covid_confirmed = pd.read_csv(COVID_CONFIRMED_URL, header = 0)
covid_confirmed.fillna(0, inplace=True)

st.subheader("Cronavirus infection across the world - " + covid_confirmed.columns[-1])
# Changing column name for latest date
covid_confirmed = covid_confirmed.rename({covid_confirmed.columns[-1]:'latest_number'}, axis = 1)
latest_number_column = covid_confirmed.columns[-1]

view = pdk.ViewState(latitude = 0, longitude = 0, zoom = 0.5)

# Create scatter(covid) layer
covidLayer = pdk.Layer(
        "ScatterplotLayer",
        data=covid_confirmed,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=1,
        radius_max_pixels=1000,
        line_width_min_pixels=2,
        get_position=['Long', 'Lat'],
        get_radius= latest_number_column,
        get_fill_color=[255,0,0],
        get_line_color=[255,0,0],
)


# Configure tooltip
TOOLTIP = {"html": "Country : {Country/Region} <br> Total Confirmed Cases : {"+latest_number_column+"}"}

# Create deck.gl map
r = pdk.Deck(
    layers = covidLayer,
    initial_view_state = view,
    map_style = "mapbox://styles/mapbox/light-v9",
    tooltip = TOOLTIP
)

# Render deck.gl map in the streamlit app as a Pydeck chart
map = st.pydeck_chart(r)

# Function to create multi chart
def draw_multichart(x, y, color, data):
    chart = alt.Chart(data).mark_line().encode(
        x = x,
        y = y,
        color = color,
        tooltip = [color, x, y]
    ).interactive().properties(
        width = 1000,
        height = 700
    )
    return chart

st.subheader("Quarterly Growth Rate of GDP in G20 Countries")
# Read GDP Data
gdp = pd.read_csv('https://raw.githubusercontent.com/yankeebreezy/Data/master/gdp.csv', header = 0)
gdp = gdp.rename({'Value':'Percentage Growth Rates of GDP'}, axis = 1)
# Plot quarterly growth rate
gdp_bar = st.altair_chart(draw_multichart('TIME', 'Percentage Growth Rates of GDP', 'Country', gdp))


st.subheader("G20 International Trade")
# Read internatinal trade data
internationalTrade = pd.read_csv('https://raw.githubusercontent.com/yankeebreezy/Data/master/international_trade.csv', header=0)
internationalTrade = internationalTrade.rename({'Value':'US Dollar, Billions'}, axis = 1)
# Plot internationa trade in a multi-line chart
internationalTrade_chart = alt.Chart(internationalTrade).mark_line().encode(
    x='TIME',
    y='US Dollar, Billions',
    color='Country',
    tooltip=['Country','TIME','US Dollar, Billions']
).interactive().properties(
    width=1000,
    height=700
)
internationalTrade_bar = st.altair_chart(draw_multichart('TIME', 'US Dollar, Billions', 'Country', internationalTrade))

def getStockMarketData():
    # yahoo finance url to download historical data
    yahoo_fin_url = 'https://query1.finance.yahoo.com/v7/finance/download/indics?period1=startdate&period2=enddate&interval=1wk&events=history'

    # Today's and Previous year date & time
    today = datetime.datetime.now()
    prevYearDateTime = today - timedelta(days=366)
    pattern = '%Y-%m-%d %H:%M:%S'
    startDate = prevYearDateTime.strftime(pattern)
    endDate = today.strftime(pattern)
    # Convert to epoch time
    startEpochTime = int(time.mktime(time.strptime(startDate,pattern)))
    endEpochTime = int(time.mktime(time.strptime(endDate,pattern)))
    stockMarketDf = pd.DataFrame()

    # Iterate indics dict to download the data
    for key,value in g20_indics.items():
        # Create a url with indics and time
        url = yahoo_fin_url.replace('indics',value).replace('startdate', str(startEpochTime)).replace('enddate', str(endEpochTime))
        # Download the individual country stock data
        countryStockData = pd.read_csv(url)
        # Create column country and indics
        countryStockData['Country'] = key
        countryStockData['Indics'] = value
        # Add data to the dataframe
        stockMarketDf = stockMarketDf.append(countryStockData)
    return stockMarketDf

stockData = getStockMarketData()

st.subheader("Stock Market Indics for major stock exchange in G20 Countries")

# Create stock market indices chart
stock_bar = st.altair_chart(draw_multichart('Date', 'Close', 'Country', stockData))


# Read inflation data
inflation_data = pd.read_csv("https://raw.githubusercontent.com/yankeebreezy/Data/master/inflation.csv", header = 0)
# Re-arrange column to row
inflation = pd.melt(inflation_data,  id_vars=['Country'], value_vars=['2014','2015','2016','2017','2018','2019','2020'])
# Rename column
inflation = inflation.rename({'variable':'Date','value':'Inflation Rate'}, axis = 1)

st.subheader("Inflation rate in G20 Countries amid Covid-19 pandemic")
# Plot multichart
inflation_bar = st.altair_chart(draw_multichart(inflation.columns[1], inflation.columns[2], inflation.columns[0], inflation))

# Read unemployment data
unemployment_data = pd.read_csv("https://raw.githubusercontent.com/yankeebreezy/Data/master/unemployment.csv", header = 0)
# Re-arrange column to row
unemp = pd.melt(unemployment_data,  id_vars=['Country'], value_vars=['2014','2015','2016','2017','2018','2019','2020'])
# Rename column
unemp = unemp.rename({'variable':'Date','value':'Unemployment Rate'}, axis = 1)

st.subheader("Unemployment rate in G20 Countries amid Covid-19 pandemic")
# Plot multichart
unemp_bar = st.altair_chart(draw_multichart(unemp.columns[1], unemp.columns[2], unemp.columns[0], unemp))



