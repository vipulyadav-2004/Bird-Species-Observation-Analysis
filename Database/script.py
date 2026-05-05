import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Avian Biodiversity Dashboard", layout="wide", page_icon="🐦")

# --- DATABASE CONNECTION ---
def get_data():
    conn = sqlite3.connect('bird_species_observations.db')
    df = pd.read_sql_query("SELECT * FROM master_bird_monitoring_data", conn)
    conn.close()
    return df

df = get_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🕊️ Bird Monitoring AI")
st.sidebar.markdown("Analyzing Forest & Grassland Ecosystems")
page = st.sidebar.selectbox("Select Analysis", ["Overview Dashboard", "Species Insights", "Environmental Trends"])

# --- PAGE 1: OVERVIEW DASHBOARD ---
if page == "Overview Dashboard":
    st.title("📊 Biodiversity Overview")
    
    # 1. Key Metrics (KPIs)
    total_obs = len(df)
    unique_species = df['Common_Name'].nunique()
    top_site = df['Admin_Unit_Code'].mode()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Observations", f"{total_obs:,}")
    col2.metric("Unique Species Identified", unique_species)
    col3.metric("Most Active Admin Unit", top_site)

    st.divider()

    # 2. Habitat Distribution (Pie Chart)
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Observation Split by Habitat")
        fig_habitat = px.pie(df, names='Habitat', hole=0.4, 
                             color_discrete_sequence=['#2E7D32', '#F9A825']) # Green for Forest, Gold for Grassland
        st.plotly_chart(fig_habitat, use_container_width=True, key="chart_one")

    with col_right:
        st.subheader("Top Observation Methods")
        # Cleaning ID_Method for display
        method_counts = df['ID_Method'].value_counts().reset_index()
        fig_method = px.bar(method_counts, x='count', y='ID_Method', orientation='h',
                            labels={'count': 'Observations', 'ID_Method': 'Method'})
        st.plotly_chart(fig_method, use_container_width=True, key="chart_two")

    # --- COORDINATES MAPPING ---
# Geographic coordinates for the Administrative Units mentioned in the dataset
park_coords = {
    'ANTI': [39.4754, -77.7441], # Antietam National Battlefield
    'CATO': [39.6465, -77.4475], # Catoctin Mountain Park
    'CHOH': [39.4216, -77.7554], # Chesapeake and Ohio Canal
    'GWMP': [38.8351, -77.0396], # George Washington Memorial Parkway
    'HAFE': [39.3248, -77.7397], # Harpers Ferry National Historical Park
    'MANA': [38.8129, -77.5147], # Manassas National Battlefield Park
    'MONO': [39.3707, -77.3917], # Monocacy National Battlefield
    'NACE': [38.8783, -76.9706], # National Capital East Parks
    'PRWI': [38.5833, -77.3667], # Prince William Forest Park
    'ROCR': [38.9431, -77.0494], # Rock Creek Park
    'WOTR': [38.9404, -77.2644]  # Wolf Trap National Park
}

# --- PAGE 1: OVERVIEW DASHBOARD ---
if page == "Overview Dashboard":
    st.title("📊 Biodiversity Overview")
    
    # 1. Key Metrics (KPIs)
    total_obs = len(df)
    unique_species = df['Common_Name'].nunique()
    top_site_code = df['Admin_Unit_Code'].mode()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Observations", f"{total_obs:,}")
    col2.metric("Unique Species Identified", unique_species)
    col3.metric("Most Active Site", top_site_code)

    st.divider()

    # 2. GEOGRAPHIC SIGHTING MAP
    st.subheader("📍 Species Observation Hotspots")
    st.markdown("Distribution of bird sightings across National Park Administrative Units.")

    # Prepare map data
    map_data = df['Admin_Unit_Code'].value_counts().reset_index()
    map_data.columns = ['Admin_Unit_Code', 'Sighting_Count']
    
    # Map lat/lon to the summary dataframe
    map_data['lat'] = map_data['Admin_Unit_Code'].map(lambda x: park_coords.get(x, [None, None])[0])
    map_data['lon'] = map_data['Admin_Unit_Code'].map(lambda x: park_coords.get(x, [None, None])[1])
    
    # Interactive Mapbox Map
    fig_map = px.scatter_mapbox(
        map_data, 
        lat="lat", 
        lon="lon", 
        size="Sighting_Count", 
        color="Sighting_Count",
        color_continuous_scale=px.colors.sequential.YlOrRd,
        hover_name="Admin_Unit_Code",
        zoom=7, 
        height=500,
        mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True , key="chart_three")

    st.divider()

    
# --- PAGE 2: SPECIES INSIGHTS ---
elif page == "Species Insights":
    st.title("🦅 Species Distribution Analysis")
    
    habitat_filter = st.radio("Select Habitat Type:", ["All", "Forest", "Grassland"], horizontal=True)
    
    filtered_df = df if habitat_filter == "All" else df[df['Habitat'] == habitat_filter]
    
    # Top 10 Species Bar Chart
    top_10 = filtered_df['Common_Name'].value_counts().head(10).reset_index()
    fig_top10 = px.bar(top_10, x='count', y='Common_Name', 
                       title=f"Top 10 Species in {habitat_filter}",
                       labels={'count': 'Observation Frequency', 'Common_Name': 'Bird Species'},
                       color='count', color_continuous_scale='Viridis')
    st.plotly_chart(fig_top10, use_container_width=True , key="chart_six")

    # Sex Ratio Analysis
    st.subheader("Species Demographics (Sex Ratio)")
    species_list = filtered_df['Common_Name'].unique()
    selected_species = st.selectbox("Select a species to view sex distribution:", species_list)
    
    sex_data = filtered_df[filtered_df['Common_Name'] == selected_species]['Sex'].value_counts().reset_index()
    fig_sex = px.pie(sex_data, names='Sex', values='count', color='Sex',
                     color_discrete_map={'Male': 'blue', 'Female': 'pink', 'Unknown': 'grey'})
    st.plotly_chart(fig_sex , key="chart_seven")
    
    # --- PAGE 3: ENVIRONMENTAL & TEMPORAL TRENDS ---
elif page == "Environmental Trends":
    st.title("🌡️ Environmental & Temporal Analysis")
    st.markdown("""
    Explore how weather conditions and time of day influence bird activity levels 
    across different habitats.
    """)

    # --- 1. Weather Correlations ---
    st.header("Weather Impact on Observations")
    env_col1, env_col2 = st.columns(2)

    with env_col1:
        st.subheader("Temperature vs. Humidity")
        # Sample data for performance if needed, or use full df
        fig_scatter = px.scatter(df.sample(min(2000, len(df))), 
                                 x='Temperature', y='Humidity', 
                                 color='Habitat', 
                                 trendline="ols",
                                 title="Temperature & Humidity Correlation")
        st.plotly_chart(fig_scatter, use_container_width=True , key="chart_eight")

    with env_col2:
        st.subheader("Observations by Sky Condition")
        sky_data = df['Sky'].value_counts().reset_index()
        fig_sky = px.bar(sky_data, x='count', y='Sky', 
                         orientation='h', color='Sky',
                         title="Sky Condition Impact")
        st.plotly_chart(fig_sky, use_container_width=True , key="chart_nine")

    st.divider()

    # --- 2. Wind and Disturbance ---
    st.subheader("Effect of Wind Conditions")
    wind_data = df['Wind'].value_counts().reset_index()
    fig_wind = px.bar(wind_data, x='Wind', y='count', 
                      color='Wind',
                      labels={'count': 'Number of Sightings'})
    st.plotly_chart(fig_wind, use_container_width=True , key="chart_ten")

    st.divider()

    # --- 3. Temporal Activity Patterns ---
    st.header("Temporal Activity Trends")
    time_col1, time_col2 = st.columns(2)

    with time_col1:
        st.subheader("Monthly/Seasonal Activity")
        # Ensure Month is extracted (from previous EDA logic)
        df['Date_dt'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date_dt'].dt.month_name()
        
        # Sort by calendar order
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        monthly_activity = df.groupby(['Month', 'Habitat']).size().reset_index(name='count')
        fig_monthly = px.line(monthly_activity, x='Month', y='count', color='Habitat',
                              category_orders={"Month": month_order},
                              markers=True, title="Sightings per Month")
        st.plotly_chart(fig_monthly, use_container_width=True , key="chart_eleven")

    with time_col2:
        st.subheader("Peak Activity Hours")
        # Using the hour extraction logic from your notebook
        def get_hour(t):
            try: return int(str(t).split(':')[0])
            except: return None
            
        df['Hour'] = df['Start_Time'].apply(get_hour)
        hourly_data = df.groupby(['Hour', 'Habitat']).size().reset_index(name='count')
        
        fig_hourly = px.area(hourly_data, x='Hour', y='count', color='Habitat',
                             title="Activity Levels by Hour of Day",
                             labels={'count': 'Observations', 'Hour': 'Hour (24h)'})
        st.plotly_chart(fig_hourly, use_container_width=True , key="chart_twelve")