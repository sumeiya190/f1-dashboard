"""
F1 Data Analysis Dashboard - Main Application
==============================================

This is the main entry point for the F1 data analysis and visualization dashboard.
Built with Streamlit for an interactive web interface.

Author: F1 Data Analysis Team
Date: November 2025
"""

import streamlit as st
import fastf1
import pandas as pd
from pathlib import Path

# Configure FastF1 cache
cache_dir = Path(__file__).parent / 'data' / 'cache'
cache_dir.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

# Page configuration
st.set_page_config(
    page_title="F1 Data Analysis Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏎️ F1 Data Analysis Dashboard")

# Welcome message
st.markdown("---")

# Introduction
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ### Welcome to the F1 Data Analysis Dashboard! 🏁
    
    This interactive dashboard provides comprehensive analysis of Formula 1 race data, 
    including lap times, telemetry, tire strategies, and more.
    
    **Get started by selecting a page from the sidebar** ⬅️
    """)

st.markdown("---")

# Features section
st.markdown("## 🎯 Key Features")

col1, col2 = st.columns(2)

with col1:
    st.info("**📊 Race Analysis**")
    st.markdown("""
    - View race results and standings
    - Analyze race pace by driver
    - Compare race strategies
    - Lap-by-lap position tracking
    """)
    
    st.info("**🔴 Live Race Tracking**")
    st.markdown("""
    - Real-time session updates
    - Live lap times and positions
    - Position change tracking
    - Auto-refresh every 30 seconds
    """)

with col2:
    st.info("**🚗 Telemetry Analysis**")
    st.markdown("""
    - Speed traces on track
    - Brake point analysis
    - Throttle and gear usage
    - Driver comparison overlays
    """)
    
    st.info("**📰 F1 News Feed**")
    st.markdown("""
    - Latest F1 news articles
    - Multiple news sources
    - Search and filter
    - Updated every 10 minutes
    """)

st.info("**📈 Tire Strategy**")
st.markdown("""
- Visualize pit stop strategies
- Tire compound usage analysis
- Tire life and degradation
- Strategy comparison
""")

st.markdown("---")

# Quick start guide
st.markdown("## 🚀 Quick Start Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ Select a Page
    Choose an analysis page from the sidebar
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Choose Race
    Select year, Grand Prix, and session type
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Explore Data
    Use interactive charts and filters
    """)

st.markdown("---")

# Available data info
with st.expander("ℹ️ Available Data & Limitations"):
    st.markdown("""
    ### Data Source
    - **Provider**: FastF1 library (official F1 timing data)
    - **Coverage**: 2018 season onwards (full telemetry)
    - **Sessions**: Practice, Qualifying, Sprint, Race
    
    ### Data Types Available
    - Lap times and sector times
    - Driver telemetry (speed, throttle, brake, gear, RPM, DRS)
    - Tire compound and age
    - Track position and coordinates
    - Weather data
    - Pit stop information
    
    ### Performance Notes
    - **First Load**: Takes 1-3 minutes to download and cache data
    - **Subsequent Loads**: Instant (data is cached locally)
    - **Cache Location**: `data/cache/`
    
    ### Known Limitations
    - Limited historical data before 2018
    - Weather data may be incomplete for some sessions
    - Telemetry data might have gaps for some drivers
    """)

# Technical info
with st.expander("🔧 Technical Information"):
    st.markdown(f"""
    ### Technology Stack
    - **Python**: 3.11+
    - **FastF1**: {fastf1.__version__}
    - **Streamlit**: Interactive web framework
    - **Plotly**: Interactive visualizations
    - **Pandas**: Data manipulation
    
    ### Cache Information
    - **Cache Directory**: `{cache_dir}`
    - **Cache Status**: ✅ Enabled
    
    ### System Requirements
    - Python 3.11 or higher
    - 2GB+ RAM recommended
    - Internet connection (for initial data download)
    - Modern web browser
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>F1 Data Analysis Dashboard</strong></p>
    <p>Built with ❤️ using FastF1, Streamlit, and Plotly</p>
    <p>For educational and analytical purposes only</p>
</div>
""", unsafe_allow_html=True)
