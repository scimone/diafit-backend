"""
Ambulatory Glucose Profile (AGP) Feature Module

This module provides functionality for calculating and analyzing
Ambulatory Glucose Profiles from CGM data.

Quick imports:
    from summary.features.agp import (
        calculate_agp_from_cgm,
        detect_agp_patterns,
        TIME_PERIODS,
    )
"""

# Configuration
# Core calculations
from .calculations import calculate_agp, calculate_agp_summary, calculate_stats
from .config import DEFAULT_TIMEZONE, POINTS_PER_DAY, POINTS_PER_HOUR, TIME_PERIODS

# Formatters
from .formatters import calculate_agp_from_cgm, format_agp_json

# Pattern detection
from .patterns import detect_agp_patterns

__all__ = [
    # Config
    "DEFAULT_TIMEZONE",
    "TIME_PERIODS",
    "POINTS_PER_HOUR",
    "POINTS_PER_DAY",
    # Calculations
    "calculate_stats",
    "calculate_agp",
    "calculate_agp_summary",
    # Formatters
    "format_agp_json",
    "calculate_agp_from_cgm",
    # Patterns
    "detect_agp_patterns",
]
