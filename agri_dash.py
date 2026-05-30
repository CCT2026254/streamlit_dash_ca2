import streamlit as st
import pandas as pd
import numpy as np

# set the browser tab title and use a wide layout so the dashboard fits on one screen
st.set_page_config(
    page_title="Ireland Agricultural Peer Dashboard",
    layout="wide"
)

# add the main dashboard title
st.title("Ireland Agricultural Peer Dashboard 🇮🇪🌾")
# add a short explanation so the user immediately understands the purpose of the dashboard
st.caption(
    "Interactive dashboard showing countries identified as agricultural peers of Ireland "
    "through Machine Learning clustering, with production and export comparisons"
)

# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lower_case = lambda x: str(x).lower()
#     data.rename(lower_case, axis="columns", inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data

# data_load_state = st.text("Loading Data ...")
# data = load_data(10000)
# data_load_state.text("Loading Data ... Done! ✅")

# st.subheader("Raw Data")
# st.write(data)

# # add histogram
# st.subheader("Number of Pickups per hour")
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

