"""
Data Loading Utilities
======================

Functions for loading and caching F1 data using FastF1.
"""

import fastf1
import pandas as pd
import streamlit as st
from typing import Optional, List, Tuple


@st.cache_data(ttl=3600)
def get_event_schedule(year: int) -> pd.DataFrame:
    """
    Get the event schedule for a specific year.
    
    Args:
        year: Championship year (e.g., 2024)
    
    Returns:
        DataFrame with event schedule
    """
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule
    except Exception as e:
        st.error(f"Error loading schedule: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_available_years() -> List[int]:
    """
    Get list of years with available F1 data.
    
    Returns:
        List of years (2018 onwards)
    """
    current_year = pd.Timestamp.now().year
    return list(range(2018, current_year + 1))


@st.cache_data(ttl=3600)
def load_session(_year: int, _gp: str, _session_type: str):
    """
    Load a specific F1 session.
    
    Args:
        _year: Championship year
        _gp: Grand Prix name or round number
        _session_type: Session type ('FP1', 'FP2', 'FP3', 'Q', 'S', 'R')
    
    Returns:
        FastF1 Session object
    """
    try:
        session = fastf1.get_session(_year, _gp, _session_type)
        
        with st.spinner(f"Loading {_session_type} session data... This may take a minute on first load."):
            session.load()
        
        return session
    except Exception as e:
        st.error(f"Error loading session: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def get_session_info(_session) -> dict:
    """
    Extract key information from a session.
    
    Args:
        _session: FastF1 Session object
    
    Returns:
        Dictionary with session information
    """
    if _session is None:
        return {}
    
    return {
        'event_name': _session.event['EventName'],
        'location': _session.event['Location'],
        'country': _session.event['Country'],
        'date': _session.event['EventDate'],
        'session_name': _session.name,
        'total_laps': len(_session.laps),
        'drivers': sorted(_session.drivers)
    }


@st.cache_data(ttl=3600)
def get_driver_info(_session, driver_code: str) -> dict:
    """
    Get information about a specific driver in a session.
    
    Args:
        _session: FastF1 Session object
        driver_code: 3-letter driver code (e.g., 'VER')
    
    Returns:
        Dictionary with driver information
    """
    if _session is None:
        return {}
    
    try:
        driver = _session.get_driver(driver_code)
        return {
            'abbreviation': driver['Abbreviation'],
            'full_name': driver['FullName'],
            'team': driver['TeamName'],
            'team_color': driver['TeamColor'],
            'driver_number': driver['DriverNumber']
        }
    except Exception as e:
        st.warning(f"Could not get info for driver {driver_code}: {str(e)}")
        return {}


@st.cache_data(ttl=3600)
def get_driver_laps(_session, driver_code: str) -> pd.DataFrame:
    """
    Get all laps for a specific driver.
    
    Args:
        _session: FastF1 Session object
        driver_code: 3-letter driver code
    
    Returns:
        DataFrame of driver laps
    """
    if _session is None:
        return pd.DataFrame()
    
    try:
        laps = _session.laps.pick_driver(driver_code)
        return laps
    except Exception as e:
        st.warning(f"Could not get laps for driver {driver_code}: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_fastest_lap(_session, driver_code: str) -> Optional[pd.Series]:
    """
    Get the fastest lap for a driver.
    
    Args:
        _session: FastF1 Session object
        driver_code: 3-letter driver code
    
    Returns:
        Series with fastest lap data or None
    """
    laps = get_driver_laps(_session, driver_code)
    if laps.empty:
        return None
    
    try:
        fastest = laps.pick_fastest()
        return fastest
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_lap_telemetry(_session, driver_code: str, lap_number: int):
    """
    Get telemetry data for a specific lap.
    
    Args:
        _session: FastF1 Session object
        driver_code: 3-letter driver code
        lap_number: Lap number
    
    Returns:
        Telemetry DataFrame
    """
    if _session is None:
        return pd.DataFrame()
    
    try:
        lap = _session.laps.pick_driver(driver_code).pick_lap(lap_number)
        telemetry = lap.get_telemetry()
        return telemetry
    except Exception as e:
        st.warning(f"Could not get telemetry: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_race_results(_session) -> pd.DataFrame:
    """
    Get race results (finishing positions).
    
    Args:
        _session: FastF1 Session object
    
    Returns:
        DataFrame with race results
    """
    if _session is None or _session.name != 'Race':
        return pd.DataFrame()
    
    try:
        results = _session.results
        return results[['Abbreviation', 'FullName', 'TeamName', 'Position', 'GridPosition', 'Points', 'Status']]
    except Exception as e:
        st.warning(f"Could not get race results: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_weather_data(_session) -> pd.DataFrame:
    """
    Get weather data for the session.
    
    Args:
        _session: FastF1 Session object
    
    Returns:
        DataFrame with weather data
    """
    if _session is None:
        return pd.DataFrame()
    
    try:
        weather = _session.weather_data
        return weather
    except Exception as e:
        st.warning(f"Could not get weather data: {str(e)}")
        return pd.DataFrame()


def format_laptime(seconds: float) -> str:
    """
    Format lap time from seconds to MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    if pd.isna(seconds):
        return "N/A"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"


def get_compound_color(compound: str) -> str:
    """
    Get the color associated with a tire compound.
    
    Args:
        compound: Tire compound name (SOFT, MEDIUM, HARD, etc.)
    
    Returns:
        Hex color code
    """
    colors = {
        'SOFT': '#FF0000',       # Red
        'MEDIUM': '#FFD700',     # Yellow
        'HARD': '#FFFFFF',       # White
        'INTERMEDIATE': '#00FF00', # Green
        'WET': '#0000FF',        # Blue
        'UNKNOWN': '#808080',    # Gray
        'TEST-UNKNOWN': '#FF69B4' # Pink
    }
    return colors.get(compound, '#808080')
