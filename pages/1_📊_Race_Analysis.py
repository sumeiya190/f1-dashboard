"""
Race Analysis Page
==================

Comprehensive race analysis including results, pace, and positions.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import (
    get_available_years,
    get_event_schedule,
    load_session,
    get_session_info,
    get_race_results,
    format_laptime
)
from utils.visualizations import (
    create_lap_time_chart,
    create_position_chart,
    create_tire_strategy_chart
)
from utils.analysis import calculate_pace_consistency

# Page config
st.set_page_config(page_title="Race Analysis", page_icon="📊", layout="wide")

st.title("📊 Race Analysis")
st.markdown("Analyze race results, lap times, and strategies")

st.markdown("---")

# Sidebar - Session Selection
st.sidebar.header("🏁 Session Selection")

# Year selection
years = get_available_years()
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)

# Get schedule
schedule = get_event_schedule(selected_year)

if not schedule.empty:
    # GP selection
    gp_names = schedule['EventName'].tolist()
    selected_gp = st.sidebar.selectbox("Select Grand Prix", gp_names)
    
    # Session type
    session_type = st.sidebar.selectbox(
        "Select Session",
        ["Race", "Qualifying", "Sprint", "FP1", "FP2", "FP3"],
        index=0
    )
    
    # Map session names
    session_map = {
        "Race": "R",
        "Qualifying": "Q",
        "Sprint": "S",
        "FP1": "FP1",
        "FP2": "FP2",
        "FP3": "FP3"
    }
    
    # Load session button
    if st.sidebar.button("📥 Load Session Data", type="primary"):
        with st.spinner("Loading session data..."):
            session = load_session(selected_year, selected_gp, session_map[session_type])
            
            if session:
                st.session_state['session'] = session
                st.session_state['session_loaded'] = True
                st.success(f"✅ Loaded {session_type} session for {selected_gp} {selected_year}")
else:
    st.error("Could not load event schedule")

# Main content
if 'session_loaded' in st.session_state and st.session_state['session_loaded']:
    session = st.session_state['session']
    
    # Session info
    info = get_session_info(session)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Location", info.get('location', 'N/A'))
    with col2:
        st.metric("🗓️ Date", info.get('date', 'N/A').strftime('%Y-%m-%d') if info.get('date') else 'N/A')
    with col3:
        st.metric("🏁 Session", info.get('session_name', 'N/A'))
    with col4:
        st.metric("📊 Total Laps", info.get('total_laps', 0))
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Results", "⏱️ Lap Times", "📈 Positions", "🛞 Tire Strategy"])
    
    with tab1:
        st.subheader("Race Results")
        
        if session.name == 'Race':
            results = get_race_results(session)
            
            if not results.empty:
                # Format results
                results_display = results.copy()
                results_display['Position'] = results_display['Position'].astype(int)
                
                st.dataframe(
                    results_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Points distribution
                st.subheader("Points Distribution")
                points_data = results_display[results_display['Points'] > 0]
                
                if not points_data.empty:
                    import plotly.express as px
                    fig = px.bar(
                        points_data,
                        x='Abbreviation',
                        y='Points',
                        color='TeamName',
                        title="Points Scored",
                        text='Points'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Race results not available")
        else:
            st.info("Results are only available for Race sessions. Select Race from the session dropdown.")
    
    with tab2:
        st.subheader("Lap Times Analysis")
        
        # Driver selection
        available_drivers = sorted(session.drivers)
        selected_drivers = st.multiselect(
            "Select Drivers to Compare (max 5)",
            available_drivers,
            default=available_drivers[:3] if len(available_drivers) >= 3 else available_drivers,
            max_selections=5
        )
        
        if selected_drivers:
            # Get lap data
            laps = session.laps
            
            # Filter for valid laps only (exclude pit laps and deleted laps)
            laps_filtered = laps[
                (laps['LapTime'].notna()) & 
                (~laps['PitOutTime'].notna()) & 
                (~laps['PitInTime'].notna())
            ].copy()
            
            # Create lap time chart
            fig = create_lap_time_chart(laps_filtered, selected_drivers)
            st.plotly_chart(fig, use_container_width=True)
            
            # Pace consistency table
            st.subheader("Pace Consistency")
            
            consistency_data = []
            for driver in selected_drivers:
                driver_laps = laps.pick_driver(driver)
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                stats = calculate_pace_consistency(lap_times)
                consistency_data.append({
                    'Driver': driver,
                    'Avg Lap Time': format_laptime(stats['mean']),
                    'Fastest Lap': format_laptime(stats['fastest']),
                    'Std Dev': f"{stats['std']:.3f}s" if stats['std'] == stats['std'] else 'N/A',
                    'Consistency %': f"{stats['coefficient_of_variation']:.2f}%" if stats['coefficient_of_variation'] == stats['coefficient_of_variation'] else 'N/A'
                })
            
            if consistency_data:
                import pandas as pd
                st.dataframe(pd.DataFrame(consistency_data), use_container_width=True, hide_index=True)
        else:
            st.info("Select at least one driver to view lap time analysis")
    
    with tab3:
        st.subheader("Position Changes")
        
        if session.name == 'Race':
            # Driver selection for position chart
            available_drivers = sorted(session.drivers)
            position_drivers = st.multiselect(
                "Select Drivers to Track (leave empty for all)",
                available_drivers,
                default=None
            )
            
            # Create position chart
            laps = session.laps
            fig = create_position_chart(laps, position_drivers if position_drivers else None)
            st.plotly_chart(fig, use_container_width=True)
            
            # Position gains/losses
            st.subheader("Position Changes Summary")
            
            results = get_race_results(session)
            if not results.empty:
                results['PositionChange'] = results['GridPosition'] - results['Position']
                gains = results[['Abbreviation', 'GridPosition', 'Position', 'PositionChange']].copy()
                gains = gains.sort_values('PositionChange', ascending=False)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Biggest Gainers 📈**")
                    st.dataframe(gains.head(5), hide_index=True)
                with col2:
                    st.markdown("**Biggest Losers 📉**")
                    st.dataframe(gains.tail(5), hide_index=True)
        else:
            st.info("Position tracking is only available for Race sessions")
    
    with tab4:
        st.subheader("Tire Strategy Analysis")
        
        # Driver selection for tire strategy
        available_drivers = sorted(session.drivers)
        strategy_drivers = st.multiselect(
            "Select Drivers to Compare Strategies",
            available_drivers,
            default=available_drivers[:5] if len(available_drivers) >= 5 else available_drivers,
            key="strategy_drivers"
        )
        
        if strategy_drivers:
            laps = session.laps
            fig = create_tire_strategy_chart(laps, strategy_drivers)
            st.plotly_chart(fig, use_container_width=True)
            
            # Pit stop summary
            st.subheader("Pit Stop Summary")
            
            for driver in strategy_drivers:
                driver_laps = laps.pick_driver(driver)
                pit_laps = driver_laps[driver_laps['PitInTime'].notna()]
                
                if not pit_laps.empty:
                    st.markdown(f"**{driver}** - {len(pit_laps)} pit stop(s)")
                    for idx, pit_lap in pit_laps.iterrows():
                        st.text(f"  Lap {pit_lap['LapNumber']}: {pit_lap['Compound']}")
        else:
            st.info("Select drivers to view tire strategy")

else:
    st.info("👈 Select a session from the sidebar and click 'Load Session Data' to begin analysis")
    
    # Show example
    st.markdown("""
    ### 📚 What You Can Analyze
    
    Once you load a session, you'll be able to:
    
    - **Results Tab**: View final standings, points distribution
    - **Lap Times Tab**: Compare driver pace and consistency
    - **Positions Tab**: Track position changes throughout the race
    - **Tire Strategy Tab**: Visualize compound choices and pit stops
    """)
