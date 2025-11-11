"""
Live Race Tracking Page
Real-time updates during active F1 sessions
"""

import streamlit as st
import fastf1
import pandas as pd
from datetime import datetime, timedelta
import time
from utils.data_loader import load_session, get_session_info
from utils.visualizations import create_position_chart, create_lap_time_chart
from utils.analysis import calculate_gap_to_leader

st.set_page_config(
    page_title="Live Race - F1 Dashboard",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 Live Race Tracker")
st.markdown("Real-time tracking of ongoing F1 sessions")

# Auto-refresh toggle
col1, col2 = st.columns([3, 1])
with col1:
    st.info("💡 Enable auto-refresh to get live updates during active sessions")
with col2:
    auto_refresh = st.checkbox("🔄 Auto-Refresh (30s)", value=False)

# Get current year and try to find ongoing session
current_year = datetime.now().year

# Session selection
st.sidebar.header("📅 Select Session")

# Get schedule
try:
    schedule = fastf1.get_event_schedule(current_year)
    
    # Find races that are happening soon or recently finished
    today = pd.Timestamp.now()
    
    # Get events within last 3 days or next 3 days
    recent_events = schedule[
        (schedule['EventDate'] >= (today - timedelta(days=3))) & 
        (schedule['EventDate'] <= (today + timedelta(days=3)))
    ]
    
    if not recent_events.empty:
        st.sidebar.success(f"🏁 Active Race Weekend!")
        
        event_options = recent_events['EventName'].tolist()
        selected_event = st.sidebar.selectbox("Select Event", event_options)
        
        event_info = recent_events[recent_events['EventName'] == selected_event].iloc[0]
    else:
        st.sidebar.warning("No active race weekend")
        # Show all events as fallback
        event_options = schedule['EventName'].tolist()
        selected_event = st.sidebar.selectbox("Select Event", event_options)
        event_info = schedule[schedule['EventName'] == selected_event].iloc[0]
    
    # Session type selection
    session_options = ['Race', 'Qualifying', 'Sprint', 'Practice 3', 'Practice 2', 'Practice 1']
    selected_session = st.sidebar.selectbox("Select Session", session_options)
    
    # Map to FastF1 session names
    session_map = {
        'Practice 1': 'FP1',
        'Practice 2': 'FP2',
        'Practice 3': 'FP3',
        'Qualifying': 'Q',
        'Sprint': 'S',
        'Race': 'R'
    }
    
    # Load button
    if st.sidebar.button("📥 Load Live Session", type="primary"):
        with st.spinner("Loading session data..."):
            try:
                session = load_session(current_year, selected_event, session_map[selected_session])
                
                if session:
                    st.session_state['live_session'] = session
                    st.session_state['live_session_loaded'] = True
                    st.success(f"✅ Loaded {selected_session} session for {selected_event}")
            except Exception as e:
                st.error(f"Could not load session: {e}")
                st.info("Session might not have started yet or data is not available")
    
except Exception as e:
    st.error(f"Error loading schedule: {e}")

# Display live session data
if 'live_session_loaded' in st.session_state and st.session_state['live_session_loaded']:
    session = st.session_state['live_session']
    
    # Session info header
    info = get_session_info(session)
    
    st.markdown("---")
    
    # Time and status metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏁 Event", info.get('location', 'N/A'))
    with col2:
        st.metric("📅 Date", info.get('date', 'N/A').strftime('%Y-%m-%d') if info.get('date') else 'N/A')
    with col3:
        st.metric("🕐 Session", info.get('session_name', 'N/A'))
    with col4:
        st.metric("📊 Total Laps", info.get('total_laps', 0))
    with col5:
        current_time = datetime.now().strftime('%H:%M:%S')
        st.metric("🕐 Current Time", current_time)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Standings", "⏱️ Lap Times", "📈 Position Changes", "🏎️ Driver Details"])
    
    with tab1:
        st.subheader("Current Standings")
        
        # Get latest laps for all drivers
        laps = session.laps
        
        if not laps.empty:
            # Get the most recent lap for each driver
            latest_laps = laps.groupby('Driver').last().reset_index()
            
            # Sort by position
            if 'Position' in latest_laps.columns:
                latest_laps = latest_laps.sort_values('Position')
            
            # Display standings
            display_cols = ['Position', 'Driver', 'LapNumber', 'LapTime']
            available_cols = [col for col in display_cols if col in latest_laps.columns]
            
            # Format lap time
            if 'LapTime' in latest_laps.columns:
                latest_laps['LapTime_Display'] = latest_laps['LapTime'].apply(
                    lambda x: f"{x.total_seconds():.3f}s" if pd.notna(x) else "N/A"
                )
                available_cols.remove('LapTime')
                available_cols.append('LapTime_Display')
            
            st.dataframe(
                latest_laps[available_cols],
                use_container_width=True,
                hide_index=True
            )
            
            # Gap to leader
            if 'Position' in latest_laps.columns and len(latest_laps) > 1:
                st.subheader("Gap to Leader")
                
                # Calculate gaps
                gaps = []
                leader_time = None
                
                for idx, row in latest_laps.iterrows():
                    if pd.notna(row.get('LapTime')):
                        current_time = row['LapTime'].total_seconds()
                        
                        if leader_time is None:
                            leader_time = current_time
                            gap = 0.0
                        else:
                            gap = current_time - leader_time
                        
                        gaps.append({
                            'Position': row.get('Position', 'N/A'),
                            'Driver': row['Driver'],
                            'Gap': f"+{gap:.3f}s" if gap > 0 else "Leader"
                        })
                
                if gaps:
                    st.dataframe(pd.DataFrame(gaps), use_container_width=True, hide_index=True)
        else:
            st.info("No lap data available yet")
    
    with tab2:
        st.subheader("Lap Time Progression")
        
        # Driver selection for lap times
        available_drivers = sorted(session.drivers)
        selected_drivers = st.multiselect(
            "Select Drivers to Track",
            available_drivers,
            default=available_drivers[:3] if len(available_drivers) >= 3 else available_drivers,
            max_selections=8,
            key="live_lap_drivers"
        )
        
        if selected_drivers and not laps.empty:
            # Filter valid laps
            laps_filtered = laps[
                (laps['LapTime'].notna()) & 
                (~laps['PitOutTime'].notna()) & 
                (~laps['PitInTime'].notna())
            ].copy()
            
            fig = create_lap_time_chart(laps_filtered, selected_drivers, title="Live Lap Times")
            st.plotly_chart(fig, use_container_width=True)
            
            # Latest lap times
            st.subheader("Latest Lap Times")
            
            latest_times = []
            for driver in selected_drivers:
                driver_laps = laps_filtered[laps_filtered['Driver'] == driver]
                if not driver_laps.empty:
                    last_lap = driver_laps.iloc[-1]
                    latest_times.append({
                        'Driver': driver,
                        'Lap': last_lap['LapNumber'],
                        'Time': f"{last_lap['LapTime'].total_seconds():.3f}s"
                    })
            
            if latest_times:
                st.dataframe(pd.DataFrame(latest_times), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Position Changes")
        
        if 'Position' in laps.columns:
            # Filter laps with valid position data
            laps_with_pos = laps[laps['Position'].notna()].copy()
            
            if not laps_with_pos.empty:
                # Show all drivers
                all_drivers = sorted(laps_with_pos['Driver'].unique())
                
                fig = create_position_chart(laps_with_pos, all_drivers)
                st.plotly_chart(fig, use_container_width=True)
                
                # Biggest gainers/losers
                st.subheader("Position Changes Summary")
                
                position_changes = []
                for driver in all_drivers:
                    driver_laps = laps_with_pos[laps_with_pos['Driver'] == driver]
                    if len(driver_laps) > 1:
                        start_pos = driver_laps.iloc[0].get('Position', None)
                        current_pos = driver_laps.iloc[-1].get('Position', None)
                        
                        if pd.notna(start_pos) and pd.notna(current_pos):
                            change = int(start_pos - current_pos)
                            position_changes.append({
                                'Driver': driver,
                                'Start': int(start_pos),
                                'Current': int(current_pos),
                                'Change': f"+{change}" if change > 0 else str(change)
                            })
                
                if position_changes:
                    df_changes = pd.DataFrame(position_changes)
                    df_changes = df_changes.sort_values('Change', ascending=False)
                    st.dataframe(df_changes, use_container_width=True, hide_index=True)
                else:
                    st.info("Not enough position data to show changes")
            else:
                st.info("Position data contains no valid values for this session")
        else:
            st.info("Position data not available for this session")
    
    with tab4:
        st.subheader("Driver Details")
        
        # Select driver for detailed view
        selected_detail_driver = st.selectbox(
            "Select Driver",
            sorted(session.drivers),
            key="detail_driver"
        )
        
        if selected_detail_driver:
            driver_laps = laps[laps['Driver'] == selected_detail_driver]
            
            if not driver_laps.empty:
                # Driver statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Laps", len(driver_laps))
                
                with col2:
                    valid_times = driver_laps[driver_laps['LapTime'].notna()]['LapTime']
                    if len(valid_times) > 0:
                        fastest = valid_times.min()
                        st.metric("Fastest Lap", f"{fastest.total_seconds():.3f}s")
                    else:
                        st.metric("Fastest Lap", "N/A")
                
                with col3:
                    if 'Position' in driver_laps.columns:
                        current_pos = driver_laps.iloc[-1].get('Position', 'N/A')
                        st.metric("Current Position", current_pos)
                    else:
                        st.metric("Current Position", "N/A")
                
                with col4:
                    pit_stops = len(driver_laps[driver_laps['PitInTime'].notna()])
                    st.metric("Pit Stops", pit_stops)
                
                # Recent laps table
                st.subheader("Recent Laps")
                
                recent_laps = driver_laps.tail(10)
                display_data = recent_laps[['LapNumber', 'LapTime', 'Compound']].copy()
                
                # Format lap time
                display_data['LapTime'] = display_data['LapTime'].apply(
                    lambda x: f"{x.total_seconds():.3f}s" if pd.notna(x) else "N/A"
                )
                
                st.dataframe(display_data, use_container_width=True, hide_index=True)
            else:
                st.info("No data available for this driver")
    
    # Auto-refresh functionality
    if auto_refresh:
        st.info("🔄 Auto-refreshing in 30 seconds...")
        time.sleep(30)
        st.rerun()

else:
    st.info("👆 Select a session from the sidebar to start live tracking")
    
    # Show helpful information
    st.markdown("### 🏁 How to Use Live Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **During Active Race Weekends:**
        - Select current event from sidebar
        - Choose session type (Race, Qualifying, etc.)
        - Click "Load Live Session"
        - Enable "Auto-Refresh" for real-time updates
        """)
    
    with col2:
        st.markdown("""
        **Features:**
        - ⏱️ Live lap times and positions
        - 📊 Real-time standings
        - 📈 Position change tracking
        - 🏎️ Individual driver statistics
        - 🔄 30-second auto-refresh option
        """)
