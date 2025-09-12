"""Statistics calculation utilities for CheerLights data."""

from collections import Counter
from datetime import datetime, timedelta
from typing import List

from ..models import ColorData, ColorStatistics


def calculate_color_statistics(colors: List[ColorData]) -> ColorStatistics:
    """Calculate statistics for a list of color data.
    
    Args:
        colors: List of ColorData objects
    
    Returns:
        ColorStatistics object with calculated statistics
    """
    if not colors:
        return ColorStatistics(
            color_counts={},
            most_popular="unknown",
            least_popular="unknown",
            total_changes=0,
            unique_colors=0,
            analysis_period="No data"
        )
    
    # Count color occurrences
    color_names = [color.color.lower() for color in colors]
    color_counts = dict(Counter(color_names))
    
    # Find most and least popular colors
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    most_popular = sorted_colors[0][0] if sorted_colors else "unknown"
    least_popular = sorted_colors[-1][0] if sorted_colors else "unknown"
    
    # Determine analysis period
    analysis_period = _determine_analysis_period(colors)
    
    return ColorStatistics(
        color_counts=color_counts,
        most_popular=most_popular,
        least_popular=least_popular,
        total_changes=len(colors),
        unique_colors=len(color_counts),
        analysis_period=analysis_period
    )


def _determine_analysis_period(colors: List[ColorData]) -> str:
    """Determine the time period covered by the color data.
    
    Args:
        colors: List of ColorData objects
    
    Returns:
        String describing the analysis period
    """
    if not colors:
        return "No data"
    
    # Try to parse timestamps to determine period
    parsed_times = []
    for color in colors:
        if color.created_at:
            parsed_times.append(color.created_at)
        else:
            # Try to parse the timestamp string
            try:
                from dateutil.parser import parse as parse_date
                parsed_time = parse_date(color.timestamp)
                parsed_times.append(parsed_time)
            except Exception:
                continue
    
    if not parsed_times:
        return f"Last {len(colors)} entries"
    
    # Sort times to get range
    parsed_times.sort()
    earliest = parsed_times[-1]  # Most recent is last in API response
    latest = parsed_times[0]     # Oldest is first in API response
    
    # Calculate time difference
    time_diff = latest - earliest
    
    if time_diff.days > 30:
        return f"{time_diff.days} days ({earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')})"
    elif time_diff.days > 1:
        return f"{time_diff.days} days"
    elif time_diff.seconds > 3600:
        hours = time_diff.seconds // 3600
        return f"{hours} hours"
    else:
        minutes = time_diff.seconds // 60
        return f"{minutes} minutes"


def find_color_transitions(colors: List[ColorData]) -> List[tuple]:
    """Find color transitions in the history.
    
    Args:
        colors: List of ColorData objects (should be in chronological order)
    
    Returns:
        List of tuples (from_color, to_color, timestamp)
    """
    if len(colors) < 2:
        return []
    
    transitions = []
    for i in range(len(colors) - 1):
        current = colors[i]
        next_color = colors[i + 1]
        
        if current.color.lower() != next_color.color.lower():
            transitions.append((current.color, next_color.color, next_color.timestamp))
    
    return transitions


def get_color_duration_stats(colors: List[ColorData]) -> dict:
    """Calculate how long each color was active.
    
    Args:
        colors: List of ColorData objects (should be in reverse chronological order)
    
    Returns:
        Dictionary with color duration statistics
    """
    if len(colors) < 2:
        return {}
    
    durations = {}
    
    for i in range(len(colors) - 1):
        current = colors[i]
        next_color = colors[i + 1]
        
        # Try to calculate duration between color changes
        try:
            if current.created_at and next_color.created_at:
                duration = current.created_at - next_color.created_at
                color_name = next_color.color.lower()
                
                if color_name not in durations:
                    durations[color_name] = []
                durations[color_name].append(duration.total_seconds())
        except Exception:
            continue
    
    # Calculate average durations
    avg_durations = {}
    for color, duration_list in durations.items():
        if duration_list:
            avg_seconds = sum(duration_list) / len(duration_list)
            avg_durations[color] = {
                "average_seconds": avg_seconds,
                "average_minutes": avg_seconds / 60,
                "occurrences": len(duration_list),
                "total_seconds": sum(duration_list)
            }
    
    return avg_durations
