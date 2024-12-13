"""
Name: Muhammad Ammar Piracha
CS 230: Section 3
Data: Nuclear Explosions 1945-1998 (2046 rows)
URL: http://localhost:8501/#nuclear-explosions-data-explorer

Description: This dataset provides a comprehensive record of nuclear explosions conducted worldwide between 1945 and 1998.
"""

import pandas as pd
import streamlit as st
# import matplotlib.pyplot as plt
# import pydeck as pdk

# Theme
# st.markdown Done with the help of ChatGPT
st.markdown(
    """
    <style>
    /* General Page Background */
    .stApp {
        background-color: black;
        color: white;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #2e2e2e;
    }

    /* Title and Subheader Styling */
    h1, h2, h3 {
        color: orange;
    }

    /* Warning Message */
    .stAlert {
        background-color: #7e2a1e; /* Dark Red for Alerts */
        color: white;
        font-weight: bold;
    }

    /* Dataframe Styling */
    .dataframe {
        border: 1px solid orange;
    }

    /* Widget styling (e.g., sliders, dropdowns) */
    .stSlider > div > div > div > div {
        background: linear-gradient(to right, darkorange, red);
    }

    /* Universal styling for all widget labels */
    label {
        color: yellow !important;
        font-weight: bold !important;
    }

    /* Customizing Button Colors */
    button {
        background-color: orange !important;
        color: black !important;
        border-radius: 5px !important;
    }

    /* Tooltip Styling */
    .tooltip {
        background-color: black;
        color: orange;
    }
    </style>
    """,
    unsafe_allow_html=True
)


data_file = "nuclear_explosions_1.csv"
data = pd.read_csv(data_file)


data_cleaned = data.dropna()
data_cleaned.columns = data_cleaned.columns.str.replace(r"[ .]", "_", regex=True).str.lower()  # Standardize column names


if 'date_year' not in data_cleaned.columns:
    if 'date' in data_cleaned.columns:

        data_cleaned['date_year'] = pd.to_datetime(data_cleaned['date'], errors='coerce').dt.year


country_column = 'weapon_source_country'


def filter_data(data, year_range=(1945, 1998), countries=None):
    if countries is None:
        countries = data[country_column].unique()
    return data[(data['date_year'] >= year_range[0]) &
                (data['date_year'] <= year_range[1]) &
                (data[country_column].isin(countries))]


st.title("Nuclear Explosions Data Explorer")

st.markdown(
    """
    This dataset provides a comprehensive record of nuclear explosions conducted worldwide 
    between 1945 and 1998. It includes key information such as:

    - Countries: The source countries responsible for the explosions.
    - Locations: Geographic coordinates and deployment sites.
    - Yields: Measured yield of explosions in kilotons (lower and upper bounds).
    - Dates: Day, month, and year of each explosion.
    - Purposes: Reasons for the explosions, such as testing or combat.

    Use the filters and visualizations below to explore historical patterns of nuclear testing and distribution.
    """)

st.sidebar.title("Filter Options")


year_range = st.sidebar.slider("Select Year Range",
                                int(data_cleaned['date_year'].min()),
                                int(data_cleaned['date_year'].max()),
                                (1945, 1998))

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=data_cleaned[country_column].unique(),
    default=data_cleaned[country_column].unique()
)


if not selected_countries:
    st.warning("Please select at least one country to view the visualizations.")
else:

    filtered_data = filter_data(data_cleaned, year_range, selected_countries)

    st.write(f"Filtered Data: {len(filtered_data)} records")
    st.dataframe(filtered_data)

    #Visualization 1
    st.subheader("Nuclear Explosions Over Time")
    trends = filtered_data.groupby('date_year').size()
    fig, ax = plt.subplots()
    trends.plot(kind='line', ax=ax, title="Nuclear Explosions Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Explosions")
    st.pyplot(fig)

    # Visualization 2
    st.subheader("Explosions by Country")
    country_counts = filtered_data[country_column].value_counts()
    fig, ax = plt.subplots()
    country_counts.plot(kind='bar', ax=ax, title="Explosions by Country")
    ax.set_xlabel("Country")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # Visualization 3
    st.subheader("Explosion Yield vs. Year")
    fig, ax = plt.subplots()
    ax.scatter(filtered_data['date_year'], filtered_data['data_yeild_upper'], color='red', alpha=0.6)
    ax.set_title("Explosion Yield vs. Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Yield (Upper)")
    st.pyplot(fig)

    # Visualization 4
    st.subheader("Explosion Locations Map")


    map_data = filtered_data[['location_cordinates_latitude', 'location_cordinates_longitude', 'weapon_source_country',
                              'data_name']].dropna()


    map_data['tooltip'] = (
            "Country: " + map_data['weapon_source_country'] + "<br>"

    )


    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_data['location_cordinates_latitude'].mean(),
            longitude=map_data['location_cordinates_longitude'].mean(),
            zoom=2,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position='[location_cordinates_longitude, location_cordinates_latitude]',
                get_radius=20000,
                get_color=[255, 0, 0],
                pickable=True,
                get_tooltip='tooltip',
            ),
        ],
        tooltip={"html": "{tooltip}", "style": {"color": "white"}},
    ))
