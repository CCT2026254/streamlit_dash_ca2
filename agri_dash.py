import streamlit as st
import pandas as pd
import numpy as np

st.title("Uber Pickups in New York City 🗽")

DATE_COLUMN = "date/time"

DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lower_case = lambda x: str(x).lower()
    data.rename(lower_case, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text("Loading Data ...")
data = load_data(10000)
data_load_state.text("Loading Data ... Done! ✅")

st.subheader("Raw Data")
st.write(data)

# add histogram
st.subheader("Number of Pickups per hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

