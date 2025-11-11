"""
Visualization Functions
=======================

Functions for creating interactive Plotly charts for F1 data.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Optional
import numpy as np


def create_lap_time_chart(laps_df: pd.DataFrame, drivers: List[str], title: str = "Lap Times Comparison") -> go.Figure:
    """
    Create an interactive lap time comparison chart.
    
    Args:
        laps_df: DataFrame with lap data
        drivers: List of driver codes to compare
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    # F1 team colors (2024 season)
    team_colors = {
        'Red Bull Racing': '#3671C6',
        'Mercedes': '#27F4D2',
        'Ferrari': '#E8002D',
        'McLaren': '#FF8000',
        'Alpine': '#FF87BC',
        'Aston Martin': '#229971',
        'RB': '#6692FF',
        'Haas F1 Team': '#B6BABD',
        'Williams': '#64C4FF',
        'Sauber': '#52E252'
    }
    
    fig = go.Figure()
    
    for driver in drivers:
        # Use pick_driver if available (FastF1 method), otherwise filter
        if hasattr(laps_df, 'pick_driver'):
            driver_laps = laps_df.pick_driver(driver)
        else:
            driver_laps = laps_df[laps_df['Driver'] == driver].copy()
        
        if driver_laps.empty:
            continue
        
        # Get lap times - FastF1 stores them as timedelta
        lap_times = driver_laps['LapTime']
        
        # Convert to seconds and remove NaN
        if hasattr(lap_times, 'dt'):
            lap_times_seconds = lap_times.dt.total_seconds()
        else:
            lap_times_seconds = lap_times
        
        # Filter valid laps
        valid_mask = lap_times_seconds.notna()
        lap_numbers = driver_laps['LapNumber'][valid_mask]
        lap_times_plot = lap_times_seconds[valid_mask]
        
        if len(lap_times_plot) == 0:
            continue
        
        # Get team color
        team_color = None
        try:
            if 'Team' in driver_laps.columns:
                team_name = driver_laps['Team'].iloc[0]
                team_color = team_colors.get(team_name, None)
        except:
            pass
        
        fig.add_trace(go.Scatter(
            x=lap_numbers,
            y=lap_times_plot,
            mode='lines+markers',
            name=str(driver),
            line=dict(color=team_color, width=2) if team_color else dict(width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{driver}</b><br>Lap: %{{x}}<br>Time: %{{y:.3f}}s<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_speed_trace_chart(telemetry_dict: dict, title: str = "Speed Trace Comparison") -> go.Figure:
    """
    Create speed trace overlay chart.
    
    Args:
        telemetry_dict: Dictionary of {driver_code: telemetry_df}
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    for driver, telemetry in telemetry_dict.items():
        if telemetry.empty or 'Distance' not in telemetry.columns or 'Speed' not in telemetry.columns:
            continue
        
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name=driver,
            line=dict(width=2),
            hovertemplate=f'<b>{driver}</b><br>Distance: %{{x:.0f}}m<br>Speed: %{{y:.0f}} km/h<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_throttle_brake_chart(telemetry: pd.DataFrame, driver: str) -> go.Figure:
    """
    Create throttle and brake trace chart.
    
    Args:
        telemetry: Telemetry DataFrame
        driver: Driver code
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    if 'Distance' not in telemetry.columns:
        return fig
    
    # Throttle trace
    if 'Throttle' in telemetry.columns:
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Throttle'],
            mode='lines',
            name='Throttle',
            line=dict(color='green', width=1),
            fill='tozeroy',
            fillcolor='rgba(0,255,0,0.3)',
            hovertemplate='Distance: %{x:.0f}m<br>Throttle: %{y}%<extra></extra>'
        ))
    
    # Brake trace
    if 'Brake' in telemetry.columns:
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Brake'],
            mode='lines',
            name='Brake',
            line=dict(color='red', width=1),
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.3)',
            hovertemplate='Distance: %{x:.0f}m<br>Brake: %{y}%<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"{driver} - Throttle & Brake Application",
        xaxis_title="Distance (m)",
        yaxis_title="Input (%)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_gear_chart(telemetry: pd.DataFrame, driver: str) -> go.Figure:
    """
    Create gear usage chart.
    
    Args:
        telemetry: Telemetry DataFrame
        driver: Driver code
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    if 'Distance' not in telemetry.columns or 'nGear' not in telemetry.columns:
        return fig
    
    fig.add_trace(go.Scatter(
        x=telemetry['Distance'],
        y=telemetry['nGear'],
        mode='lines',
        name='Gear',
        line=dict(color='purple', width=2),
        fill='tozeroy',
        fillcolor='rgba(128,0,128,0.3)',
        hovertemplate='Distance: %{x:.0f}m<br>Gear: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{driver} - Gear Usage",
        xaxis_title="Distance (m)",
        yaxis_title="Gear",
        yaxis=dict(range=[0, 8], dtick=1),
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig


def create_tire_strategy_chart(laps_df: pd.DataFrame, drivers: List[str]) -> go.Figure:
    """
    Create tire strategy visualization.
    
    Args:
        laps_df: DataFrame with lap and tire data
        drivers: List of driver codes
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    compound_colors = {
        'SOFT': '#FF0000',
        'MEDIUM': '#FFD700',
        'HARD': '#FFFFFF',
        'INTERMEDIATE': '#00FF00',
        'WET': '#0000FF'
    }
    
    for i, driver in enumerate(drivers):
        # Use pick_driver if available
        if hasattr(laps_df, 'pick_driver'):
            driver_laps = laps_df.pick_driver(driver)
        else:
            driver_laps = laps_df[laps_df['Driver'] == driver].copy()
        
        if driver_laps.empty or 'Compound' not in driver_laps.columns:
            continue
        
        # Group consecutive laps with same compound
        driver_laps['CompoundChange'] = driver_laps['Compound'] != driver_laps['Compound'].shift()
        driver_laps['Stint'] = driver_laps['CompoundChange'].cumsum()
        
        for stint, stint_data in driver_laps.groupby('Stint'):
            compound = stint_data['Compound'].iloc[0]
            # Handle NaN compounds
            if pd.isna(compound):
                compound = 'UNKNOWN'
            
            start_lap = stint_data['LapNumber'].iloc[0]
            end_lap = stint_data['LapNumber'].iloc[-1]
            
            fig.add_trace(go.Scatter(
                x=[start_lap, end_lap],
                y=[i, i],
                mode='lines',
                name=f'{driver} - {compound}',
                line=dict(
                    color=compound_colors.get(str(compound).upper(), '#808080'),
                    width=20
                ),
                showlegend=True,
                hovertemplate=f'<b>{driver}</b><br>Compound: {compound}<br>Laps: {start_lap}-{end_lap}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Tire Strategy Comparison",
        xaxis_title="Lap Number",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(drivers))),
            ticktext=drivers,
            title="Driver"
        ),
        hovermode='closest',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_position_chart(laps_df: pd.DataFrame, drivers: Optional[List[str]] = None) -> go.Figure:
    """
    Create position changes chart over race.
    
    Args:
        laps_df: DataFrame with position data
        drivers: Optional list of drivers to highlight
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Check if required columns exist
    if 'Position' not in laps_df.columns or 'LapNumber' not in laps_df.columns:
        fig.add_annotation(
            text="Position data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter out rows with NaN positions
    laps_with_pos = laps_df[laps_df['Position'].notna()].copy()
    
    if laps_with_pos.empty:
        fig.add_annotation(
            text="No position data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    all_drivers = laps_with_pos['Driver'].unique()
    drivers_to_plot = drivers if drivers else all_drivers
    
    # Get team colors
    team_colors = {
        'Red Bull Racing': '#3671C6',
        'Mercedes': '#27F4D2',
        'Ferrari': '#E8002D',
        'McLaren': '#FF8000',
        'Aston Martin': '#229971',
        'Alpine': '#FF87BC',
        'Williams': '#64C4FF',
        'RB': '#6692FF',
        'Kick Sauber': '#52E252',
        'Haas F1 Team': '#B6BABD'
    }
    
    for driver in drivers_to_plot:
        driver_data = laps_with_pos[laps_with_pos['Driver'] == driver].copy()
        
        if driver_data.empty:
            continue
        
        # Get team color
        color = None
        if 'Team' in driver_data.columns:
            team_name = driver_data['Team'].iloc[0]
            color = team_colors.get(team_name, None)
        
        if not color and 'TeamColor' in driver_data.columns:
            color = driver_data['TeamColor'].iloc[0]
            if color and not color.startswith('#'):
                color = f'#{color}'
        
        fig.add_trace(go.Scatter(
            x=driver_data['LapNumber'],
            y=driver_data['Position'],
            mode='lines+markers',
            name=driver,
            line=dict(color=color, width=2) if color else dict(width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{driver}</b><br>Lap: %{{x}}<br>Position: %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Position Changes During Race",
        xaxis_title="Lap Number",
        yaxis_title="Position",
        yaxis=dict(autorange='reversed'),  # Position 1 at top
        hovermode='x unified',
        template='plotly_dark',
        height=500
    )
    
    return fig


def create_sector_times_chart(laps_df: pd.DataFrame, drivers: List[str]) -> go.Figure:
    """
    Create sector times comparison chart.
    
    Args:
        laps_df: DataFrame with sector time data
        drivers: List of driver codes
    
    Returns:
        Plotly Figure object
    """
    sector_cols = ['Sector1Time', 'Sector2Time', 'Sector3Time']
    available_sectors = [col for col in sector_cols if col in laps_df.columns]
    
    if not available_sectors:
        return go.Figure()
    
    fig = go.Figure()
    
    for driver in drivers:
        driver_laps = laps_df[laps_df['Driver'] == driver]
        
        if driver_laps.empty:
            continue
        
        sector_times = []
        sector_names = []
        
        for i, sector_col in enumerate(available_sectors, 1):
            best_time = driver_laps[sector_col].min()
            if pd.notna(best_time):
                sector_times.append(best_time.total_seconds() if hasattr(best_time, 'total_seconds') else best_time)
                sector_names.append(f'Sector {i}')
        
        if sector_times:
            fig.add_trace(go.Bar(
                name=driver,
                x=sector_names,
                y=sector_times,
                text=[f'{t:.3f}s' for t in sector_times],
                textposition='auto',
                hovertemplate=f'<b>{driver}</b><br>%{{x}}: %{{y:.3f}}s<extra></extra>'
            ))
    
    fig.update_layout(
        title="Best Sector Times Comparison",
        xaxis_title="Sector",
        yaxis_title="Time (seconds)",
        barmode='group',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_speed_heatmap(telemetry: pd.DataFrame, driver: str) -> go.Figure:
    """
    Create speed heatmap visualization.
    
    Args:
        telemetry: Telemetry DataFrame with X, Y, Speed columns
        driver: Driver code
    
    Returns:
        Plotly Figure object
    """
    if 'X' not in telemetry.columns or 'Y' not in telemetry.columns or 'Speed' not in telemetry.columns:
        return go.Figure()
    
    fig = go.Figure(data=go.Scatter(
        x=telemetry['X'],
        y=telemetry['Y'],
        mode='markers',
        marker=dict(
            size=3,
            color=telemetry['Speed'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Speed (km/h)")
        ),
        hovertemplate='Speed: %{marker.color:.0f} km/h<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{driver} - Speed Trace on Track",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        template='plotly_white',
        height=600,
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )
    
    return fig


def create_lap_time_distribution(laps_df: pd.DataFrame, drivers: List[str]) -> go.Figure:
    """
    Create lap time distribution (violin/box plot).
    
    Args:
        laps_df: DataFrame with lap times
        drivers: List of driver codes
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    for driver in drivers:
        driver_laps = laps_df[laps_df['Driver'] == driver]
        
        if driver_laps.empty or 'LapTime' not in driver_laps.columns:
            continue
        
        lap_times = driver_laps['LapTime'].dt.total_seconds().dropna()
        
        fig.add_trace(go.Violin(
            y=lap_times,
            name=driver,
            box_visible=True,
            meanline_visible=True,
            hovertemplate=f'<b>{driver}</b><br>Time: %{{y:.3f}}s<extra></extra>'
        ))
    
    fig.update_layout(
        title="Lap Time Distribution",
        yaxis_title="Lap Time (seconds)",
        template='plotly_white',
        height=500
    )
    
    return fig
