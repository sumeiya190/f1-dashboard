"""
Analysis Functions
==================

Functions for analyzing F1 data and calculating metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict


def calculate_lap_time_delta(lap1_time: float, lap2_time: float) -> float:
    """
    Calculate the time difference between two laps.
    
    Args:
        lap1_time: First lap time in seconds
        lap2_time: Second lap time in seconds
    
    Returns:
        Time delta in seconds (positive if lap2 is faster)
    """
    return lap1_time - lap2_time


def calculate_pace_consistency(lap_times: pd.Series) -> Dict[str, float]:
    """
    Calculate pace consistency metrics for a driver.
    
    Args:
        lap_times: Series of lap times in seconds
    
    Returns:
        Dictionary with consistency metrics
    """
    valid_laps = lap_times.dropna()
    
    if len(valid_laps) < 2:
        return {
            'mean': np.nan,
            'std': np.nan,
            'coefficient_of_variation': np.nan,
            'fastest': np.nan,
            'slowest': np.nan
        }
    
    return {
        'mean': valid_laps.mean(),
        'std': valid_laps.std(),
        'coefficient_of_variation': (valid_laps.std() / valid_laps.mean()) * 100,
        'fastest': valid_laps.min(),
        'slowest': valid_laps.max()
    }


def calculate_tire_degradation(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate tire degradation for each stint.
    
    Args:
        laps_df: DataFrame with lap data including TyreLife and LapTime
    
    Returns:
        DataFrame with degradation analysis
    """
    if 'TyreLife' not in laps_df.columns or 'LapTime' not in laps_df.columns:
        return pd.DataFrame()
    
    # Group by tire age
    degradation = laps_df.groupby('TyreLife').agg({
        'LapTime': ['mean', 'min', 'count']
    }).reset_index()
    
    degradation.columns = ['TyreLife', 'AvgLapTime', 'FastestLapTime', 'LapCount']
    
    return degradation


def identify_outliers(lap_times: pd.Series, threshold: float = 1.5) -> pd.Series:
    """
    Identify outlier lap times using IQR method.
    
    Args:
        lap_times: Series of lap times
        threshold: IQR multiplier for outlier detection
    
    Returns:
        Boolean series indicating outliers
    """
    Q1 = lap_times.quantile(0.25)
    Q3 = lap_times.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    
    return (lap_times < lower_bound) | (lap_times > upper_bound)


def calculate_sector_analysis(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze sector times for each driver.
    
    Args:
        laps_df: DataFrame with sector time columns
    
    Returns:
        DataFrame with sector analysis
    """
    sector_cols = ['Sector1Time', 'Sector2Time', 'Sector3Time']
    
    # Check if sector columns exist
    available_sectors = [col for col in sector_cols if col in laps_df.columns]
    
    if not available_sectors:
        return pd.DataFrame()
    
    analysis = pd.DataFrame()
    
    for sector in available_sectors:
        sector_data = laps_df[sector].dropna()
        if len(sector_data) > 0:
            analysis[f'{sector}_fastest'] = [sector_data.min()]
            analysis[f'{sector}_mean'] = [sector_data.mean()]
    
    return analysis


def calculate_speed_trap_stats(telemetry_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate speed statistics from telemetry.
    
    Args:
        telemetry_df: DataFrame with Speed column
    
    Returns:
        Dictionary with speed statistics
    """
    if 'Speed' not in telemetry_df.columns:
        return {}
    
    speeds = telemetry_df['Speed'].dropna()
    
    return {
        'max_speed': speeds.max(),
        'avg_speed': speeds.mean(),
        'min_speed': speeds.min(),
        'top_5_percent': speeds.quantile(0.95)
    }


def calculate_brake_points(telemetry_df: pd.DataFrame, threshold: float = 50) -> pd.DataFrame:
    """
    Identify brake points from telemetry.
    
    Args:
        telemetry_df: DataFrame with Brake and Distance columns
        threshold: Brake pressure threshold to identify braking
    
    Returns:
        DataFrame with brake point locations
    """
    if 'Brake' not in telemetry_df.columns or 'Distance' not in telemetry_df.columns:
        return pd.DataFrame()
    
    # Identify where braking starts
    braking = telemetry_df['Brake'] > threshold
    brake_starts = braking & ~braking.shift(1, fill_value=False)
    
    brake_points = telemetry_df[brake_starts][['Distance', 'Speed', 'Brake']]
    
    return brake_points


def compare_telemetry_delta(telemetry1: pd.DataFrame, telemetry2: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate delta between two telemetry traces.
    
    Args:
        telemetry1: First driver's telemetry
        telemetry2: Second driver's telemetry
    
    Returns:
        DataFrame with delta calculations
    """
    if telemetry1.empty or telemetry2.empty:
        return pd.DataFrame()
    
    # Merge on distance
    merged = pd.merge_asof(
        telemetry1[['Distance', 'Speed']].rename(columns={'Speed': 'Speed1'}),
        telemetry2[['Distance', 'Speed']].rename(columns={'Speed': 'Speed2'}),
        on='Distance',
        direction='nearest'
    )
    
    merged['SpeedDelta'] = merged['Speed1'] - merged['Speed2']
    
    return merged


def calculate_pit_stop_delta(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate time lost/gained during pit stops.
    
    Args:
        laps_df: DataFrame with pit stop information
    
    Returns:
        DataFrame with pit stop analysis
    """
    if 'PitInTime' not in laps_df.columns or 'PitOutTime' not in laps_df.columns:
        return pd.DataFrame()
    
    pit_laps = laps_df[laps_df['PitInTime'].notna()].copy()
    
    if pit_laps.empty:
        return pd.DataFrame()
    
    pit_laps['PitDuration'] = (pit_laps['PitOutTime'] - pit_laps['PitInTime']).dt.total_seconds()
    
    return pit_laps[['LapNumber', 'Compound', 'PitDuration', 'TyreLife']]


def calculate_race_pace(laps_df: pd.DataFrame, exclude_first_laps: int = 3) -> pd.DataFrame:
    """
    Calculate race pace excluding outliers and first laps.
    
    Args:
        laps_df: DataFrame with lap data
        exclude_first_laps: Number of initial laps to exclude
    
    Returns:
        DataFrame with race pace metrics
    """
    # Exclude first laps and outliers
    valid_laps = laps_df[laps_df['LapNumber'] > exclude_first_laps].copy()
    
    if 'LapTime' not in valid_laps.columns:
        return pd.DataFrame()
    
    # Remove outliers
    lap_times = valid_laps['LapTime'].dt.total_seconds()
    outliers = identify_outliers(lap_times)
    valid_laps = valid_laps[~outliers]
    
    # Calculate pace by compound
    pace_by_compound = valid_laps.groupby('Compound').agg({
        'LapTime': ['count', 'mean', 'std', 'min']
    }).reset_index()
    
    pace_by_compound.columns = ['Compound', 'LapCount', 'AvgLapTime', 'StdDev', 'FastestLap']
    
    return pace_by_compound


def calculate_overtakes(position_data: pd.DataFrame) -> pd.DataFrame:
    """
    Identify overtakes from position data.
    
    Args:
        position_data: DataFrame with lap-by-lap positions
    
    Returns:
        DataFrame with overtake information
    """
    if 'Position' not in position_data.columns or 'LapNumber' not in position_data.columns:
        return pd.DataFrame()
    
    overtakes = []
    
    for i in range(1, len(position_data)):
        prev_pos = position_data.iloc[i-1]['Position']
        curr_pos = position_data.iloc[i]['Position']
        
        if prev_pos > curr_pos:  # Gained positions
            overtakes.append({
                'LapNumber': position_data.iloc[i]['LapNumber'],
                'FromPosition': prev_pos,
                'ToPosition': curr_pos,
                'PositionsGained': prev_pos - curr_pos
            })
    
    return pd.DataFrame(overtakes)


def calculate_qualifying_progression(session_laps: pd.DataFrame) -> pd.DataFrame:
    """
    Track qualifying progression (Q1, Q2, Q3 best times).
    
    Args:
        session_laps: DataFrame with qualifying lap data
    
    Returns:
        DataFrame with best time progression
    """
    if 'LapTime' not in session_laps.columns or 'Driver' not in session_laps.columns:
        return pd.DataFrame()
    
    # Get best lap for each driver
    best_laps = session_laps.loc[session_laps.groupby('Driver')['LapTime'].idxmin()]
    
    return best_laps.sort_values('LapTime')[['Driver', 'LapTime', 'Compound', 'LapNumber']]


def calculate_gap_to_leader(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate time gap to race leader for each lap.
    
    Args:
        laps_df: DataFrame with lap times and positions
    
    Returns:
        DataFrame with gap calculations
    """
    if 'LapTime' not in laps_df.columns or 'Position' not in laps_df.columns:
        return pd.DataFrame()
    
    gaps = []
    
    for lap_num in laps_df['LapNumber'].unique():
        lap_data = laps_df[laps_df['LapNumber'] == lap_num].copy()
        leader_time = lap_data[lap_data['Position'] == 1]['LapTime'].iloc[0] if len(lap_data) > 0 else None
        
        if leader_time:
            lap_data['GapToLeader'] = (lap_data['LapTime'] - leader_time).dt.total_seconds()
            gaps.append(lap_data)
    
    return pd.concat(gaps) if gaps else pd.DataFrame()
