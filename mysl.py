


import streamlit as st

st.title("HWstreamlit_6030816421")
st.markdown("Date&Hours")
select_date = st.sidebar.selectbox('Date :' , ['01/01/2019','02/01/2019','03/01/2019','04/01/2019','05/01/2019'])

if select_date=='01/01/2019':
    DATA_URL = ("https://raw.githubusercontent.com/warm9441/Streamlit2/master/ODsample/01012019.csv")
elif select_date=='02/01/2019':
    DATA_URL = ("https://raw.githubusercontent.com/warm9441/Streamlit2/master/ODsample/02012019.csv")
elif select_date=='03/01/2019':
    DATA_URL = ("https://raw.githubusercontent.com/warm9441/Streamlit2/master/ODsample/03012019.csv")
elif select_date=='04/01/2019':
    DATA_URL = ("https://raw.githubusercontent.com/warm9441/Streamlit2/master/ODsample/04012019.csv")
elif select_date=='05/01/2019':
    DATA_URL = ("https://raw.githubusercontent.com/warm9441/Streamlit2/master/ODsample/05012019.csv")

import pandas as pd

DATE_TIME = "timestart"
st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME],format='%d/%m/%Y %H:%M')
    return data
data = load_data(100000)


hour = st.sidebar.slider("Hours", 0, 23,step=4)
data = data[data[DATE_TIME].dt.hour == hour]


if st.checkbox("Show raw data", False):
    '## Raw data at %sh' % hour,data

import geopandas as gp

crs = "EPSG:4326"
geometry = gp.points_from_xy(data.lonstartl,data.latstartl)
geo_df  = gp.GeoDataFrame(data,crs=crs,geometry=geometry)

import folium as fo


st.subheader("Map at %i:00" %hour)
longitude = 100.523186
latitude = 13.736717
station_map = fo.Map(
                location = [latitude, longitude], 
                zoom_start = 10)

latitudes = list(data.latstartl)
longitudes = list(data.lonstartl)
time = list(data.timestart)
labels = list(data.n)

from streamlit_folium import folium_static


for lat, lon,t, label in zip(latitudes, longitudes,time, labels):
    if data.timestart[label].hour==hour and data.timestart[label].year!=2018:
        fo.Marker(
          location = [lat, lon], 
          popup = [label,lat,lon,t],
          icon = fo.Icon(color='black', icon='map-marker')
         ).add_to(station_map)
folium_static(station_map)

import numpy as np

st.subheader("Geo data between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latstartl"]), np.average(data["lonstartl"]))

import pydeck as pdk

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=["lonstartl", "latstartl"],
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

import altair as alt

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)
