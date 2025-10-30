import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# Page configuration
st.set_page_config(page_title="Bangalore EV Charging - Real-Time", layout="wide", page_icon="⚡")

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .location-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    .blink {
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker {
        50% { opacity: 0.5; }
    }
    </style>
""", unsafe_allow_html=True)

# Bangalore location data with strategic EV charging station locations
@st.cache_data
def get_bangalore_locations():
    locations = pd.DataFrame({
        'Location Name': [
            'Koramangala (Proposed)',
            'Whitefield Tech Park (Proposed)',
            'Indiranagar Main (Proposed)',
            'Electronic City Phase 1 (Proposed)',
            'MG Road Metro (Proposed)',
            'HSR Layout (Proposed)',
            'Yeshwanthpur Metro (Proposed)',
            'Bellandur ORR (Proposed)',
            'Hebbal Flyover (Proposed)',
            'JP Nagar (Proposed)',
            'Malleshwaram (Proposed)',
            'Sarjapur Road (Proposed)',
            'KR Puram Railway (Proposed)',
            'Airport Road (Proposed)',
            'Jayanagar 4th Block (Proposed)'
        ],
        'Latitude': [12.9352, 12.9698, 12.9716, 12.8456, 12.9716, 12.9116, 13.0280, 12.9266, 13.0358, 12.9088, 13.0032, 12.9100, 13.0054, 13.0569, 12.9250],
        'Longitude': [77.6245, 77.7499, 77.6412, 77.6603, 77.5946, 77.6382, 77.5558, 77.6799, 77.5971, 77.5850, 77.5701, 77.6970, 77.6966, 77.6412, 77.5833],
        'Area Type': [
            'Residential + Commercial',
            'IT Hub',
            'Commercial + Residential',
            'IT Hub',
            'Metro Station + Commercial',
            'Residential + Commercial',
            'Metro Station + Transport Hub',
            'IT Hub + Highway',
            'Highway Junction',
            'Residential',
            'Residential + Commercial',
            'IT Hub + Residential',
            'Railway Station + Industrial',
            'Airport Corridor',
            'Residential + Commercial'
        ],
        'Priority': ['High', 'Very High', 'High', 'Very High', 'Very High', 'High', 'High', 'Very High', 'High', 'Medium', 'Medium', 'Very High', 'High', 'Very High', 'Medium'],
        'Estimated Daily Traffic': [8500, 12000, 9500, 15000, 11000, 7500, 9000, 13000, 10000, 6500, 6000, 11500, 8000, 14000, 6800],
        'Nearby Landmarks': [
            'Forum Mall, Restaurants',
            'ITPL, Tech Parks',
            'Metro, CMH Road',
            'Infosys Campus, Tech Parks',
            'MG Road Metro, Brigade Road',
            'BDA Complex, Parks',
            'Metro Station, Railway',
            'Eco Space, Manyata Tech Park',
            'Metro, Manyata Tech Park',
            'Metro Station, Residential',
            'Orion Mall, Residential',
            'Tech Parks, Restaurants',
            'Railway Station',
            'Manyata Tech Park',
            'Commercial Street nearby'
        ],
        'Recommended Chargers': [12, 20, 15, 25, 18, 10, 15, 22, 16, 8, 8, 20, 12, 24, 10],
        'Investment (Lakhs)': [180, 300, 225, 375, 270, 150, 225, 330, 240, 120, 120, 300, 180, 360, 150],
        'Expected ROI (months)': [18, 14, 16, 12, 15, 20, 18, 13, 16, 22, 21, 14, 19, 13, 20]
    })
    return locations

# Generate real-time operational data
def generate_realtime_data():
    """Generate simulated real-time data"""
    np.random.seed(int(time.time()))  # Use current time for randomness
    
    # Existing stations in Bangalore with real-time status
    existing_stations = pd.DataFrame({
        'Station ID': ['BLR-001', 'BLR-002', 'BLR-003'],
        'Location': ['Koramangala 5th Block', 'Whitefield', 'Electronic City'],
        'Status': ['Active', 'Active', 'Active'],
        'Chargers': [10, 15, 12],
        'Available': np.random.randint(2, 8, 3),
        'In Use': [0, 0, 0],  # Will be calculated
        'Power (kW)': [150, 200, 180],
        'Utilization': [0, 0, 0],  # Will be calculated
        'Current Load (kW)': np.random.randint(50, 150, 3),
        'Temperature (°C)': np.random.randint(28, 45, 3)
    })
    
    # Calculate in use and utilization
    existing_stations['In Use'] = existing_stations['Chargers'] - existing_stations['Available']
    existing_stations['Utilization'] = (existing_stations['In Use'] / existing_stations['Chargers'] * 100).round(1)
    
    # Time series data for last 30 days plus today
    dates = pd.date_range(end=datetime.now(), periods=31, freq='D')
    
    daily_data = pd.DataFrame({
        'Date': dates,
        'Energy (kWh)': np.random.randint(800, 2500, 31),
        'Sessions': np.random.randint(80, 200, 31),
        'Revenue (₹)': np.random.randint(15000, 45000, 31),
        'Avg Duration (min)': np.random.randint(35, 75, 31)
    })
    
    # Real-time metrics for today
    realtime_metrics = {
        'current_power': np.random.randint(250, 450),
        'active_sessions': np.random.randint(8, 25),
        'today_energy': np.random.randint(1200, 1800),
        'today_revenue': np.random.randint(25000, 35000),
        'queue_waiting': np.random.randint(0, 8),
        'avg_wait_time': np.random.randint(5, 25)
    }
    
    return existing_stations, daily_data, realtime_metrics

# Initialize session state for auto-refresh
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

locations_df = get_bangalore_locations()

# Header with real-time indicator
col1, col2 = st.columns([6, 1])
with col1:
    st.title("⚡ Bangalore EV Charging Station - Real-Time Dashboard")
    st.markdown("**Strategic location planning for EV charging infrastructure across Bengaluru**")
with col2:
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"<div style='text-align: right; padding-top: 20px;'><span class='blink' style='color: #10b981; font-size: 24px;'>●</span> <b>LIVE</b><br>{current_time}</div>", unsafe_allow_html=True)

# Auto-refresh settings in sidebar
st.sidebar.header("⚙️ Real-Time Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)

if auto_refresh:
    st.sidebar.success(f"Auto-refreshing every {refresh_interval}s")
    # Auto-rerun after specified interval
    time.sleep(refresh_interval)
    st.rerun()
else:
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()

st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

# Generate real-time data
existing_stations_df, daily_df, realtime_metrics = generate_realtime_data()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔴 Live Monitor", "📍 Location Map", "📊 Location Analysis", "💰 Investment Analysis", "📈 Historical Data"])

# TAB 1: REAL-TIME MONITORING
with tab1:
    st.header("🔴 Live Station Monitoring")
    
    # Real-time Key Metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("⚡ Current Power", f"{realtime_metrics['current_power']} kW", 
                 delta=f"{np.random.randint(-50, 50)} kW")
    with col2:
        st.metric("🔌 Active Sessions", realtime_metrics['active_sessions'],
                 delta=f"{np.random.randint(-3, 5)}")
    with col3:
        st.metric("📊 Today's Energy", f"{realtime_metrics['today_energy']} kWh",
                 delta=f"{np.random.randint(50, 200)} kWh")
    with col4:
        st.metric("💰 Today's Revenue", f"₹{realtime_metrics['today_revenue']:,}",
                 delta=f"₹{np.random.randint(500, 2000):,}")
    with col5:
        st.metric("⏳ Queue Waiting", realtime_metrics['queue_waiting'],
                 delta=f"{np.random.randint(-2, 3)}")
    with col6:
        st.metric("⏱️ Avg Wait Time", f"{realtime_metrics['avg_wait_time']} min",
                 delta=f"{np.random.randint(-5, 5)} min")
    
    st.divider()
    
    # Live station status
    st.subheader("🏢 Live Station Status")
    
    for idx, station in existing_stations_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            
            with col1:
                status_color = "#10b981" if station['Status'] == 'Active' else "#ef4444"
                st.markdown(f"### <span style='color: {status_color};'>●</span> {station['Location']}", unsafe_allow_html=True)
                st.caption(f"Station ID: {station['Station ID']}")
            
            with col2:
                st.metric("Available", station['Available'], delta=f"of {station['Chargers']}")
            
            with col3:
                util_color = "#10b981" if station['Utilization'] < 70 else "#f97316"
                st.markdown(f"**Utilization**<br><span style='font-size: 24px; color: {util_color};'>{station['Utilization']}%</span>", unsafe_allow_html=True)
            
            with col4:
                st.metric("In Use", station['In Use'])
            
            with col5:
                st.metric("Load", f"{station['Current Load (kW)']} kW")
            
            with col6:
                temp_color = "#10b981" if station['Temperature (°C)'] < 40 else "#ef4444"
                st.markdown(f"**Temp**<br><span style='font-size: 24px; color: {temp_color};'>{station['Temperature (°C)']}°C</span>", unsafe_allow_html=True)
            
            # Progress bar for utilization
            st.progress(station['Utilization'] / 100)
        
        st.divider()
    
    # Real-time power consumption chart
    st.subheader("⚡ Real-Time Power Consumption")
    
    # Generate last 60 seconds of data
    time_points = pd.date_range(end=datetime.now(), periods=60, freq='s')
    power_data = pd.DataFrame({
        'Time': time_points,
        'Power (kW)': np.random.randint(200, 500, 60)
    })
    
    fig_realtime = go.Figure()
    fig_realtime.add_trace(go.Scatter(
        x=power_data['Time'],
        y=power_data['Power (kW)'],
        mode='lines',
        line=dict(color='#667eea', width=2),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    fig_realtime.update_layout(
        height=300,
        xaxis_title="Time",
        yaxis_title="Power (kW)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_realtime, use_container_width=True)
    
    # Active charging sessions
    st.subheader("🔌 Active Charging Sessions")
    
    active_sessions = pd.DataFrame({
        'Vehicle ID': [f'KA{np.random.randint(1, 99):02d}EV{np.random.randint(1000, 9999)}' for _ in range(realtime_metrics['active_sessions'])],
        'Station': np.random.choice(existing_stations_df['Location'].values, realtime_metrics['active_sessions']),
        'Start Time': [(datetime.now() - timedelta(minutes=np.random.randint(5, 60))).strftime('%H:%M') for _ in range(realtime_metrics['active_sessions'])],
        'Duration': [f"{np.random.randint(5, 60)} min" for _ in range(realtime_metrics['active_sessions'])],
        'Charged (kWh)': np.random.randint(5, 50, realtime_metrics['active_sessions']),
        'Status': ['Charging' for _ in range(realtime_metrics['active_sessions'])],
        'Progress': np.random.randint(20, 95, realtime_metrics['active_sessions'])
    })
    
    st.dataframe(active_sessions, width='stretch', hide_index=True)

# TAB 2: Location Map (same as before)
with tab2:
    st.header("Proposed EV Charging Station Locations in Bangalore")
    
    priority_filter = st.multiselect(
        "Filter by Priority",
        options=['Very High', 'High', 'Medium'],
        default=['Very High', 'High', 'Medium']
    )
    
    filtered_locations = locations_df[locations_df['Priority'].isin(priority_filter)]
    
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11)
    color_map = {'Very High': 'red', 'High': 'orange', 'Medium': 'blue'}
    
    for idx, row in filtered_locations.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(f"""
                <b>{row['Location Name']}</b><br>
                Priority: {row['Priority']}<br>
                Area: {row['Area Type']}<br>
                Daily Traffic: {row['Estimated Daily Traffic']:,}<br>
                Chargers: {row['Recommended Chargers']}<br>
                Investment: ₹{row['Investment (Lakhs)']} L<br>
                ROI: {row['Expected ROI (months)']} months<br>
                Landmarks: {row['Nearby Landmarks']}
            """, max_width=300),
            tooltip=row['Location Name'],
            icon=folium.Icon(color=color_map[row['Priority']], icon='charging-station', prefix='fa')
        ).add_to(m)
    
    st_folium(m, height=800, width=1400, returned_objects=[])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔴 **Very High Priority** - High traffic IT hubs, Metro stations")
    with col2:
        st.markdown("🟠 **High Priority** - Major commercial + residential areas")
    with col3:
        st.markdown("🔵 **Medium Priority** - Residential areas with moderate traffic")

# TAB 3: Location Analysis (same as before)
with tab3:
    st.header("📊 Detailed Location Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Proposed Locations", len(locations_df))
    with col2:
        st.metric("Total Chargers Planned", locations_df['Recommended Chargers'].sum())
    with col3:
        st.metric("Avg Daily Traffic", f"{locations_df['Estimated Daily Traffic'].mean():,.0f}")
    with col4:
        st.metric("Total Investment", f"₹{locations_df['Investment (Lakhs)'].sum():.0f} L")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Locations by Priority")
        priority_counts = locations_df['Priority'].value_counts()
        fig_priority = go.Figure(data=[go.Pie(
            labels=priority_counts.index,
            values=priority_counts.values,
            marker=dict(colors=['#ef4444' if x=='Very High' else '#f97316' if x=='High' else '#3b82f6' for x in priority_counts.index])
        )])
        fig_priority.update_layout(height=350)
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        st.subheader("Area Type Distribution")
        area_types = locations_df['Area Type'].value_counts()
        fig_area = go.Figure(data=[go.Bar(
            x=area_types.index,
            y=area_types.values,
            marker=dict(color=area_types.values, colorscale='Viridis')
        )])
        fig_area.update_layout(
            height=350,
            xaxis_title="Area Type",
            yaxis_title="Number of Locations",
            showlegend=False
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    st.subheader("Daily Traffic Analysis by Location")
    sorted_locs = locations_df.sort_values('Estimated Daily Traffic', ascending=True)
    fig_traffic = go.Figure()
    
    for priority in ['Medium', 'High', 'Very High']:
        priority_data = sorted_locs[sorted_locs['Priority'] == priority]
        color = '#3b82f6' if priority == 'Medium' else '#f97316' if priority == 'High' else '#ef4444'
        fig_traffic.add_trace(go.Bar(
            y=priority_data['Location Name'],
            x=priority_data['Estimated Daily Traffic'],
            name=priority,
            orientation='h',
            marker=dict(color=color)
        ))
    
    fig_traffic.update_layout(height=500, barmode='overlay')
    st.plotly_chart(fig_traffic, use_container_width=True)
    
    st.subheader("Complete Location Details")
    st.dataframe(locations_df, width='stretch', height=400)

# TAB 4: Investment Analysis (same as before)
with tab4:
    st.header("💰 Investment & ROI Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Investment Required", f"₹{locations_df['Investment (Lakhs)'].sum():.0f} L")
    with col2:
        st.metric("Avg Investment per Location", f"₹{locations_df['Investment (Lakhs)'].mean():.0f} L")
    with col3:
        st.metric("Avg ROI Period", f"{locations_df['Expected ROI (months)'].mean():.0f} months")
    with col4:
        st.metric("Best ROI Location", locations_df.loc[locations_df['Expected ROI (months)'].idxmin(), 'Location Name'].split('(')[0])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Investment vs Expected ROI")
        fig_roi = go.Figure()
        
        for priority in ['Medium', 'High', 'Very High']:
            priority_data = locations_df[locations_df['Priority'] == priority]
            color = '#3b82f6' if priority == 'Medium' else '#f97316' if priority == 'High' else '#ef4444'
            fig_roi.add_trace(go.Scatter(
                x=priority_data['Investment (Lakhs)'],
                y=priority_data['Expected ROI (months)'],
                mode='markers',
                name=priority,
                marker=dict(
                    size=priority_data['Recommended Chargers'],
                    color=color,
                    sizemode='diameter',
                    sizeref=2
                ),
                text=priority_data['Location Name'],
                hovertemplate='<b>%{text}</b><br>Investment: ₹%{x}L<br>ROI: %{y} months<extra></extra>'
            ))
        
        fig_roi.update_layout(height=400)
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        st.subheader("Investment Distribution")
        top_locations = locations_df.sort_values('Investment (Lakhs)', ascending=False).head(10)
        fig_invest = go.Figure()
        
        for priority in ['Medium', 'High', 'Very High']:
            priority_data = top_locations[top_locations['Priority'] == priority]
            color = '#3b82f6' if priority == 'Medium' else '#f97316' if priority == 'High' else '#ef4444'
            fig_invest.add_trace(go.Bar(
                x=priority_data['Location Name'],
                y=priority_data['Investment (Lakhs)'],
                name=priority,
                marker=dict(color=color)
            ))
        
        fig_invest.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_invest, use_container_width=True)
    
    st.subheader("Investment Breakdown by Priority")
    priority_investment = locations_df.groupby('Priority').agg({
        'Investment (Lakhs)': 'sum',
        'Recommended Chargers': 'sum',
        'Location Name': 'count'
    }).round(2)
    priority_investment.columns = ['Total Investment (Lakhs)', 'Total Chargers', 'Number of Locations']
    st.dataframe(priority_investment, width='stretch')
    
    st.subheader("🎯 Top 5 Locations by ROI")
    best_roi = locations_df.nsmallest(5, 'Expected ROI (months)')[['Location Name', 'Priority', 'Investment (Lakhs)', 'Expected ROI (months)', 'Estimated Daily Traffic']]
    st.dataframe(best_roi, width='stretch', hide_index=True)

# TAB 5: Historical Data
with tab5:
    st.header("📈 Historical Performance Data")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Stations", len(existing_stations_df))
    with col2:
        st.metric("Total Chargers", existing_stations_df['Chargers'].sum())
    with col3:
        st.metric("Available Now", existing_stations_df['Available'].sum())
    with col4:
        st.metric("Avg Utilization", f"{existing_stations_df['Utilization'].mean():.1f}%")
    
    st.divider()
    
    st.subheader("Current Stations")
    st.dataframe(existing_stations_df[['Station ID', 'Location', 'Status', 'Chargers', 'Available', 'In Use', 'Utilization']], width='stretch', hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Energy Consumption (30 Days)")
        fig_energy = go.Figure()
        fig_energy.add_trace(go.Scatter(
            x=daily_df['Date'],
            y=daily_df['Energy (kWh)'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ))
        fig_energy.update_layout(height=350)
        st.plotly_chart(fig_energy, use_container_width=True)
    
    with col2:
        st.subheader("Daily Revenue (₹)")
        fig_revenue = go.Figure(data=[go.Bar(
            x=daily_df['Date'],
            y=daily_df['Revenue (₹)'],
            marker=dict(
                color=daily_df['Revenue (₹)'],
                colorscale='Greens'
            )
        )])
        fig_revenue.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.subheader("Charging Sessions Trend")
    fig_sessions = px.line(
        daily_df,
        x='Date',
        y='Sessions',
        markers=True
    )
    fig_sessions.update_layout(height=300)
    st.plotly_chart(fig_sessions, use_container_width=True)

# Footer
st.divider()
st.caption(f"🔴 LIVE Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: {'ON' if auto_refresh else 'OFF'}")