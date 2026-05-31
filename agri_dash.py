import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# set the browser tab title and use a wide layout so the dashboard fits on one screen
st.set_page_config(page_title="Ireland Agricultural Peer Dashboard", layout="wide")

# add the main dashboard title
st.title("Ireland Agricultural Peer Dashboard 🇮🇪🌾")
# add a short explanation so the user immediately understands the purpose of the dashboard
st.caption(
    "Interactive dashboard showing countries identified as agricultural peers of Ireland "
    "through Machine Learning clustering, with production and export comparisons"
)

# create a list of countries to display on the map
peer_countries = [
    {"country": "Ireland", "map_label": "Ireland", "iso_alpha": "IRL", "role": "Ireland"},
    {"country": "United Kingdom", "map_label": "UK", "iso_alpha": "GBR", "role": "Peer country"},
    {"country": "Australia", "map_label": "Australia", "iso_alpha": "AUS", "role": "Peer country"},
    {"country": "New Zealand", "map_label": "New Zealand", "iso_alpha": "NZL", "role": "Peer country"},
    {"country": "Uruguay", "map_label": "Uruguay", "iso_alpha": "URY", "role": "Peer country"},
]

# convert the list of dictionaries into a pandas dataframe
peer_df = pd.DataFrame(peer_countries)

# create a list of selectable peer countries (i.e. exclude Ireland)
peer_options = peer_df.loc[peer_df["country"] != "Ireland", "country"].tolist()


## Create two main dashboard columns:
# - the left column holds the radio buttons, map, and legend(?)
# - the right column holds a compact summary of the selected peer
map_col, summary_col = st.columns([2.3, 1])

## Map column: radio buttons to select peer country + worldmap
with map_col:
    st.markdown("**Select peer country for comparison with Ireland:**")

    # add horizontal radio buttons above the map
    selected_peer = st.radio(
        label="Peer country",
        options=peer_options,
        index=0,
        horizontal=True,
        label_visibility="collapsed"
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

    # display the name of selected country
    selected_iso = peer_df.loc[peer_df["country"] == selected_peer, "iso_alpha"].iloc[0]
    selected_map_label = peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]
    # this is a text layer placed over the filled country map
    fig.add_trace(
        go.Scattergeo(
            locations=[selected_iso],
            locationmode="ISO-3",
            text=[selected_map_label],
            mode="text",
            textfont=dict(size=15, color="black"),
            showlegend=False,
            hoverinfo="skip"
        )
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
        # these ranges focus the map on Europe, Australia, Uruguay and New Zealand
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
        height=430,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    # display the map in Streamlit.
    st.plotly_chart(fig, width="stretch")


### Show Irelan's and selected country's Agricultural land stats (from the latest year available) in summary panel on the right
# cache the land dataset so Streamlit does not reload it after every interaction
@st.cache_data
def load_land_data():
    land_df = pd.read_csv("land_df.csv")
    return land_df

# load land-use data
land_df = load_land_data()

# format land values for display.
def format_land_value(value):
    return f"{value*1000:,.0f} ha"    # the data unit is 1,000 hectares

# get the land-use row for a selected country and year
def get_land_row(country_name, year=2023):
    # filter the land dataframe to the selected country and year
    country_year_df = land_df[(land_df["country_name"] == country_name) & (land_df["year"] == year)]
    return country_year_df.iloc[0]

# create a small land-use pie chart for one country
def create_land_pie_chart(row, display_name):
    # calculate Permanent crops = Cropland - Arable land
    permanent_crops = row["cropland_ha"] - row["arable_land_ha"]

    # create a small dataframe for the pie chart
    pie_df = pd.DataFrame({
        "land_type": ["Arable land", "Permanent crops", "Permanent meadows and pastures"],
        "value": [row["arable_land_ha"], permanent_crops, row["permanent_meadows_and_pastures_ha"]]})

    # create the pie chart
    fig = px.pie(pie_df, names="land_type", values="value", hole=0.35) #, title=display_name)
    # keep the pie chart compact for the right-side summary panel
    fig.update_layout(height=230, margin=dict(l=50, r=0, t=0, b=0), showlegend=True, legend_title_text="")

    # make the hover labels easier to read
    fig.update_traces(textinfo="percent",
        hovertemplate="%{label}<br>%{value:,.0f} ha<br>%{percent}<extra></extra>"
    )
    return fig

# show the land summary for one country
def show_land_summary(display_name, land_country_name):

    row = get_land_row(land_country_name, year=2023)

    # show country name and agricultural land as the card title
    st.markdown(f"**{display_name}: {format_land_value(row['agricultural_land_ha'])}**")

    # create and display the pie chart
    fig = create_land_pie_chart(row, display_name)

    st.plotly_chart(fig, width="stretch") #, config={"displayModeBar": False})


## Summary of Irelan's and selected country's agri land
#  - total area ha (from the latest year available =2023)
#  - small pie chart with agri land structure
with summary_col:
    st.subheader("Agricultural land (2023)")

    # get the selected peer row from peer_df
    selected_peer_row = peer_df.loc[peer_df["country"] == selected_peer].iloc[0]

    # show Ireland first as the fixed baseline
    ireland_row = peer_df.loc[peer_df["country"] == "Ireland"].iloc[0]
    show_land_summary(display_name="Ireland", land_country_name=ireland_row["country"])

    # show the selected peer country
    show_land_summary(display_name=selected_peer_row["country"], land_country_name=selected_peer_row["country"])