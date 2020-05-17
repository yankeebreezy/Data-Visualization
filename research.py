import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pydeck as pdk
import altair as alt

COVID_CONFIRMED_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

covid_confirmed = pd.read_csv(COVID_CONFIRMED_URL, header = 0)
covid_confirmed.fillna(0, inplace=True)
st.write(covid_confirmed[1:10])

gdp = pd.read_csv("DP_LIVE_16052020154134076.csv")
gdp = gdp[gdp.LOCATION != 'OECD']
st.write(gdp[1:10])

st.write(pd.read_csv("GH5050 Covid-19 sex-disaggregated data tracker.csv").head())

#st.write(pd.read_excel("WEO_Data.xls").head())

last_date = covid_confirmed.columns[-1]
covid_confirmed_last_updated = covid_confirmed[['Country/Region','Lat','Long', last_date]]
covid_confirmed_last_updated[last_date] = covid_confirmed_last_updated[last_date].astype(int)

view = pdk.ViewState(latitude = 0, longitude = 0, zoom = 0.2)

# Create scatter(covid) layer
covidLayer = pdk.Layer(
        "ScatterplotLayer",
        data=covid_confirmed_last_updated,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=500,
        radius_min_pixels=1,
        radius_max_pixels=1000000000,
        line_width_min_pixels=2,
        get_position=['Long', 'Lat'],
        get_radius= last_date,
        get_fill_color=[255,0,0],
        get_line_color=[255,0,0],
)
# Configure tooltip
TOOLTIP = {"html": "Country : {Country/Region} <br> Total Confirmed Cases : {5/16/20}"}

# Create deck.gl map
r = pdk.Deck(
    layers = covidLayer,
    initial_view_state = view,
    map_style = "mapbox://styles/mapbox/light-v9",
    tooltip = TOOLTIP
)

# Render deck.gl map in the streamlit app as a Pydeck chart
map = st.pydeck_chart(r)

# Custom Altair line chart where you set color and specify dimensions
custom_chart = alt.Chart(gdp).mark_line().encode(
    x='TIME',
    y='Value',
    color='LOCATION'
).properties(
    width=900,
    height=500
)

st.altair_chart(custom_chart)


unemployment_data = pd.read_csv("unemployment.csv")
st.write(unemployment_data)
inflation_data = pd.read_csv("inflation.csv")
st.write(inflation_data)