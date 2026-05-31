import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# set the browser tab title and use a wide layout so the dashboard fits on one screen
st.set_page_config(page_title="Ireland Agricultural Peer Dashboard", layout="wide")

# add the main dashboard title
st.title("Ireland Agricultural Peer Dashboard 🇮🇪")
# add a short explanation so the user immediately understands the purpose of the dashboard
st.caption(
    "Interactive dashboard showing countries identified as agricultural peers of Ireland "
    "through Machine Learning clustering, with production and export comparisons"
)

# create a list of countries to display on the map
peer_countries = [
    {"country": "Ireland", "map_label": "Ireland", "iso_alpha": "IRL", "role": "Ireland"},
    {"country": "United Kingdom of Great Britain and Northern Ireland", "map_label": "UK", "iso_alpha": "GBR", "role": "Peer country"},
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
            "Other peer": "oldlace"        # light orange
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
        lonaxis_range=[-80, 180],
        lataxis_range=[-70, 65]
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
# cache the datasets so Streamlit does not reload them after every interaction
@st.cache_data
def load_data():
    land_df = pd.read_csv("land_df.csv")
    prod_df = pd.read_csv("prod_df.csv")
    export_df = pd.read_csv("export_df.csv")
    return land_df, prod_df, export_df
# load data
land_df, prod_df, export_df = load_data()

# define fixed colours for land-use categories
land_type_colours = {
    "Arable land": "#11a0aa",                      
    "Permanent crops": "#c9ca8e",                  
    "Perm. meadows and pastures": "#86cc31"}

# format land values for display.
def format_land_value(value):
    value_ha = value * 1000
    return f"{value_ha:,.0f} ha"    # the data unit is 1,000 hectares

# get the land-use row for a selected country and year
def get_land_row(country_name, year=2023):
    # filter the land dataframe to the selected country and year
    country_year_df = land_df[(land_df["country_name"] == country_name) & (land_df["year"] == year)]
    return country_year_df.iloc[0]

# create a small land-use pie chart for one country
def create_land_pie_chart(row):
    # calculate Permanent crops = Cropland - Arable land
    permanent_crops = (row["cropland_ha"] - row["arable_land_ha"]) * 1000

    # create a small dataframe for the pie chart
    pie_df = pd.DataFrame({
        "land_type": ["Arable land", "Permanent crops", "Perm. meadows and pastures"],
        "value": [row["arable_land_ha"]*1000, permanent_crops, row["permanent_meadows_and_pastures_ha"]*1000]})

    # create the pie chart
    fig = px.pie(pie_df, names="land_type", values="value", color="land_type", color_discrete_map=land_type_colours, hole=0.35)
    # keep the pie chart compact for the right-side summary panel
    fig.update_layout(height=170, margin=dict(l=50, r=0, t=0, b=0), showlegend=True, legend_title_text="")

    # make the hover labels easier to read
    fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:,.0f} ha<br>%{percent}<extra></extra>")
    return fig

# show the land summary for one country
def show_land_summary(display_name, land_country_name):

    row = get_land_row(land_country_name, year=2023)

    # show country name and agricultural land as the card title
    st.markdown(f"**{display_name}: {format_land_value(row['agricultural_land_ha'])}**")

    # create and display the pie chart
    fig = create_land_pie_chart(row)

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


### Production data display
# Define production groups for the dashboard
production_groups = {
    "Crops 🌾🥔": {"Barley": "barley_prod_t", "Cereals": "cereals_n_e_c_prod_t", "Oats": "oats_prod_t", "Potatoes": "potatoes_prod_t", "Pulses": "pulses_total_prod_t", "Vegetables": "vegetables_primary_prod_t", "Wheat": "wheat_prod_t"},
    "Dairy products 🧀🍶": {"Butter": "butter_of_cow_milk_prod_t", "Cheese": ["cheese_from_milk_of_goats_prod_t", "cheese_from_milk_of_sheep_prod_t", "cheese_from_skimmed_cow_milk_prod_t", "cheese_from_whole_cow_milk_prod_t"], "Cream": "cream_fresh_prod_t", "Milk": ["skim_milk_condensed_prod_t", "whole_milk_condensed_prod_t", "whole_milk_powder_prod_t", "skim_milk_and_whey_powder_prod_t"]},
    "Meat & eggs 🥩🥚": {"Hen eggs": "hen_eggs_in_shell_fresh_prod_t", "Cattle meat": "meat_of_cattle_prod_t", "Chicken meat": "meat_of_chickens_prod_t", "Goat meat": "meat_of_goat_prod_t", "Pig meat": "meat_of_pig_prod_t", "Sheep meat": "meat_of_sheep_prod_t"}}

# Format large production values for chart text and hover labels
def format_tonnes(value):
    # return a compact tonnes label
    return f"{value:,.0f} t"

# get the production value for one country row and one dashboard item
def get_production_value(row, column_or_columns):
    # if the item is based on a list of columns, aggregate them
    if isinstance(column_or_columns, list):
        return row[column_or_columns].sum(skipna=True, min_count=1)     # min_count=1 means the result is NaN if all source columns are missing

    # otherwise, return the single column value
    return row[column_or_columns]

# build the long-format dataframe needed for one production chart
def build_production_chart_data(selected_peer, selected_year, group_name):
    # get Ireland's country name
    ireland_name = peer_df.loc[peer_df["country"] == "Ireland", "country"].iloc[0]
    # get selected peer's country name
    selected_peer_name = peer_df.loc[peer_df["country"] == selected_peer, "country"].iloc[0]
    # create a mapping from production dataset names to dashboard display names
    country_display_names = {ireland_name: "Ireland", selected_peer_name: peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]}
    # filter production data to Ireland, selected peer, and selected year
    year_df = prod_df[(prod_df["year"] == selected_year) & (prod_df["country_name"].isin([ireland_name, selected_peer_name]))]
    # prepare an empty list for chart rows
    chart_rows = []

    # Loop through each country row
    for _, row in year_df.iterrows():
        # get the country name used for display in the chart
        display_country = country_display_names[row["country_name"]]

        # loop through each product in the selected group and calculate the production value
        for product_label, column_or_columns in production_groups[group_name].items():
            value = get_production_value(row, column_or_columns)
            # add the value to the chart data
            chart_rows.append({"country": display_country, "product": product_label, "production_t": value})

    # convert chart rows into a dataframe
    chart_df = pd.DataFrame(chart_rows)
    # remove rows where production is missing
    chart_df = chart_df.dropna(subset=["production_t"])
    # return the chart dataframe
    return chart_df


# create one production bar chart
def create_production_bar_chart(chart_df, group_name, selected_year):
    # get the short display label for the selected peer
    selected_peer_label = peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]
    # create a horizontal grouped bar chart
    fig = px.bar(chart_df, y="product", x="production_t", color="country", orientation="h", barmode="group", title=f"{group_name}", labels={"product": "", "production_t": "Production (tonnes)", "country": "Country"}, color_discrete_map={"Ireland": "green", selected_peer_label: "darkorange"})
    # keep the chart compact
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=35, b=0), legend_title_text="", xaxis_tickformat=",", title_x=0.5, title_xanchor="center")
    # show exact values on hover
    fig.update_traces(hovertemplate="%{y}<br>%{x:,.0f} tonnes<extra></extra>")
    # return the finished figure
    return fig


## Below map and countries' summary add two tabs to display Production and Export data
production_tab, export_tab = st.tabs(["Production", "Export"])
# we'll only show data for recent years (2015-2023), also known as used for clustering
production_start_year = 2015
production_end_year = 2023

with production_tab:
    st.markdown(
        "Production comparison between Ireland and the selected peer country. "
        "Use the year slider to compare the production structure for a specific year.")
    # filter the available production years to the selected dashboard period
    available_production_years = sorted(prod_df.loc[ prod_df["year"].between(production_start_year, production_end_year), "year"].dropna().unique())

    # create a year slider using the available production years
    selected_year = st.slider("Select production year:", min_value=int(min(available_production_years)), max_value=int(max(available_production_years)), value=int(max(available_production_years)), step=1)

    # create three columns for the three product groups
    crop_col, dairy_col, meat_col = st.columns(3)

    # build and display the crops chart
    with crop_col:
        crop_df = build_production_chart_data(selected_peer=selected_peer, selected_year=selected_year, group_name="Crops 🌾🥔")
        crop_fig = create_production_bar_chart(chart_df=crop_df, group_name="Crops 🌾🥔", selected_year=selected_year)
        st.plotly_chart(crop_fig, width="stretch", config={"displayModeBar": False})

    # build and display the dairy chart
    with dairy_col:
        dairy_df = build_production_chart_data(selected_peer=selected_peer, selected_year=selected_year, group_name="Dairy products 🧀🍶")
        dairy_fig = create_production_bar_chart(chart_df=dairy_df, group_name="Dairy products 🧀🍶", selected_year=selected_year)
        st.plotly_chart(dairy_fig, width="stretch", config={"displayModeBar": False})

    # build and display the meat and eggs chart
    with meat_col:
        meat_df = build_production_chart_data(selected_peer=selected_peer, selected_year=selected_year, group_name="Meat & eggs 🥩🥚")
        meat_fig = create_production_bar_chart(chart_df=meat_df, group_name="Meat & eggs 🥩🥚", selected_year=selected_year)
        st.plotly_chart(meat_fig, width="stretch",config={"displayModeBar": False})



### Export data display (similar to production data display)
# Define export groups for the dashboard
export_groups = {
    "Crops 🌾🥔": {"Barley": "barley_export_value_ths_usd", "Oats": "oats_export_value_ths_usd",  "Rolled oats": "oats_rolled_export_value_ths_usd", "Potatoes": "potatoes_export_value_ths_usd", "Vegetable products": "vegetable_products_export_value_ths_usd", "Fresh/frozen vegetables": ["other_vegetables_fresh_export_value_ths_usd", "vegetables_frozen_export_value_ths_usd"], "Wheat": "wheat_export_value_ths_usd"},
    "Dairy products 🧀🍶": { "Butter": "butter_of_cow_milk_export_value_ths_usd", "Cheese": ["cheese_from_milk_of_sheep_export_value_ths_usd", "cheese_from_whole_cow_milk_export_value_ths_usd"], "Cream": "cream_fresh_export_value_ths_usd", "Raw milk": "raw_milk_of_cattle_export_value_ths_usd", "Milk powders/condensed": ["skim_milk_and_whey_powder_export_value_ths_usd", "skim_milk_condensed_export_value_ths_usd", "whole_milk_condensed_export_value_ths_usd", "whole_milk_powder_export_value_ths_usd"], "Skim milk": "skim_milk_of_cows_export_value_ths_usd", "Other dairy": "dairy_products_export_value_ths_usd"},
    "Meat & eggs 🥩🥚": {"Hen eggs": "hen_eggs_in_shell_fresh_export_value_ths_usd", "Liquid eggs": "eggs_liquid_export_value_ths_usd", "Cattle meat": ["meat_of_cattle_boneless_export_value_ths_usd", "meat_of_cattle_with_the_bone_export_value_ths_usd"], "Chicken meat": "meat_of_chickens_export_value_ths_usd", "Pig meat": ["meat_of_pig_boneless_export_value_ths_usd", "meat_of_pig_with_the_bone_export_value_ths_usd"], "Sheep meat": "meat_of_sheep_export_value_ths_usd", "Goat meat": "meat_of_goat_export_value_ths_usd"}}

# format total export value from thousand usd to readable usd
def format_export_value(value_ths_usd):
    value_usd = value_ths_usd * 1000
    return f"${value_usd / 1_000_000_000:.1f}bn" if value_usd >= 1_000_000_000 else f"${value_usd / 1_000_000:.1f}m"

# get export value from one column or sum several columns
def get_export_value(row, column_or_columns):
    if isinstance(column_or_columns, list):
        existing_columns = [col for col in column_or_columns if col in export_df.columns]
        return row[existing_columns].sum(skipna=True, min_count=1) if existing_columns else None
    return row[column_or_columns] if column_or_columns in export_df.columns else None

# get one country-year row
def get_export_row(country, year):
    country_year_df = export_df[(export_df["country_name"] == country) & (export_df["year"] == year)]
    return None if country_year_df.empty else country_year_df.iloc[0]

# build chart data for one export group
def build_export_chart_data(selected_peer, selected_year, group_name):
    selected_peer_label = peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]
    country_display_names = {"Ireland": "Ireland", selected_peer: selected_peer_label}
    year_df = export_df[(export_df["year"] == selected_year) & (export_df["country_name"].isin(["Ireland", selected_peer]))]
    chart_rows = []
    for _, row in year_df.iterrows():
        for product_label, column_or_columns in export_groups[group_name].items():
            value_ths_usd = get_export_value(row, column_or_columns)
            chart_rows.append({"country": country_display_names[row["country_name"]], "product": product_label, "export_value_m_usd": value_ths_usd / 1000 if pd.notna(value_ths_usd) else None})
    return pd.DataFrame(chart_rows).dropna(subset=["export_value_m_usd"])

# create one export bar chart
def create_export_bar_chart(chart_df, group_name, selected_peer):
    selected_peer_label = peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]
    fig = px.bar(chart_df, y="product", x="export_value_m_usd", color="country", orientation="h", barmode="group", title=group_name, labels={"product": "", "export_value_m_usd": "Export value (million USD)", "country": "Country"}, color_discrete_map={"Ireland": "green", selected_peer_label: "darkorange"})
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=45, b=0), legend_title_text="", xaxis_tickformat=",", paper_bgcolor="rgba(0,0,0,0)", title_x=0.5, title_xanchor="center")
    fig.update_traces(hovertemplate="%{y}<br>$%{x:,.1f} million<extra></extra>")
    return fig

with export_tab:
    st.markdown("Export comparison between Ireland and the selected peer country. Values are shown in million USD.")

    # keep export years aligned with the recent analysis period
    available_export_years = sorted(export_df.loc[export_df["year"].between(2015, 2024), "year"].dropna().unique())
    selected_export_year = st.slider("Select export year", min_value=int(min(available_export_years)), max_value=int(max(available_export_years)), value=int(max(available_export_years)), step=1, key="export_year")

    # show total agricultural export value for ireland and selected peer
    selected_peer_label = peer_df.loc[peer_df["country"] == selected_peer, "map_label"].iloc[0]
    ireland_export_row = get_export_row("Ireland", selected_export_year)
    peer_export_row = get_export_row(selected_peer, selected_export_year)
    total_col_1, total_col_2 = st.columns(2)

    with total_col_1:
        if ireland_export_row is not None:
            st.metric(label=f"Ireland total agri export value ({selected_export_year})", value=format_export_value(ireland_export_row["crops_and_livestock_products_export_value_ths_usd"]))

    with total_col_2:
        if peer_export_row is not None:
            st.metric(label=f"{selected_peer_label} total agri export value ({selected_export_year})", value=format_export_value(peer_export_row["crops_and_livestock_products_export_value_ths_usd"]))

    # show export structure by product group
    export_crop_col, export_dairy_col, export_meat_col = st.columns(3)

    with export_crop_col:
        export_crop_df = build_export_chart_data(selected_peer, selected_export_year, "Crops 🌾🥔")
        export_crop_fig = create_export_bar_chart(export_crop_df, "Crops 🌾🥔", selected_peer)
        st.plotly_chart(export_crop_fig, width="stretch", config={"displayModeBar": False})

    with export_dairy_col:
        export_dairy_df = build_export_chart_data(selected_peer, selected_export_year, "Dairy products 🧀🍶")
        export_dairy_fig = create_export_bar_chart(export_dairy_df, "Dairy products 🧀🍶", selected_peer)
        st.plotly_chart(export_dairy_fig, width="stretch", config={"displayModeBar": False})

    with export_meat_col:
        export_meat_df = build_export_chart_data(selected_peer, selected_export_year, "Meat & eggs 🥩🥚")
        export_meat_fig = create_export_bar_chart(export_meat_df, "Meat & eggs 🥩🥚", selected_peer)
        st.plotly_chart(export_meat_fig, width="stretch", config={"displayModeBar": False})