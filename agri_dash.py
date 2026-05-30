import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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

# create a list of countries to display on the map
peer_countries = [
    {"country": "Ireland", "iso_alpha": "IRL", "role": "Ireland"},
    {"country": "United Kingdom", "iso_alpha": "GBR", "role": "Peer country"},
    {"country": "Australia", "iso_alpha": "AUS", "role": "Peer country"},
    {"country": "New Zealand", "iso_alpha": "NZL", "role": "Peer country"},
    {"country": "Uruguay", "iso_alpha": "URY", "role": "Peer country"},
]

# convert the list of dictionaries into a pandas dataframe
peer_df = pd.DataFrame(peer_countries)

# create a list of selectable peer countries (i.e. exclude Ireland)
peer_options = peer_df.loc[peer_df["country"] != "Ireland", "country"].tolist()

# add horizontal radio buttons above the map
selected_peer = st.radio(
    "Select peer country for comparison with Ireland:",
    peer_options,
    index=0,
    horizontal=True
)

# create a display role column to control how each country is coloured on the map
peer_df["display_role"] = "Other peer"

# mark Ireland as the fixed baseline country
peer_df.loc[peer_df["country"] == "Ireland", "display_role"] = "Ireland"

# mark the peer country selected in the sidebar
peer_df.loc[peer_df["country"] == selected_peer, "display_role"] = "Selected peer"


# create a filled country map
fig = px.choropleth(
    peer_df,
    locations="iso_alpha",
    locationmode="ISO-3",
    color="display_role",
    hover_name="country",
    color_discrete_map={
        "Ireland": "green",          # green
        "Selected peer": "darkorange",    # stronger orange
        "Other peer": "bisque"        # light orange
    },
    # title="Ireland and Selected Agricultural Peer Country"
)
# Improve the map appearance with natural Earth look
fig.update_geos(
    projection_type="natural earth",
    showcountries=True,
    countrycolor="white",     # white country borders
    showcoastlines=True,
    coastlinecolor="white",
    showland=True,
    landcolor="whitesmoke",      # very light grey for non-peer countries
    showframe=False,

    # These ranges focus the map on Europe, Australia, and New Zealand.
    # This avoids most of the Americas after Uruguay is removed.
    lonaxis_range=[-70, 180],
    lataxis_range=[-60, 65]
)

# add subtle borders around the filled peer countries
fig.update_traces(
    marker_line_color="white",
    marker_line_width=0.8
)

# set a fixed figure size so the map is larger but not stretched across the full screen
fig.update_layout(
    width=950,
    height=600,
    margin=dict(l=0, r=0, t=50, b=0),
    showlegend=False
)

# display the map in Streamlit.
st.plotly_chart(fig, width="content")




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

