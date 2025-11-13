"""
DEPRECATED: This module has been refactored and moved.

The AGP feature has been moved to summary.features.agp

Please update your imports:
- from summary.features.agp import TIME_PERIODS, DEFAULT_TIMEZONE
- from summary.features.agp import calculate_agp, calculate_stats, calculate_agp_summary
- from summary.features.agp import calculate_agp_from_cgm, format_agp_json
- from summary.features.agp import detect_agp_patterns

Or use the convenience import:
- from summary.features.agp import (
    calculate_agp_from_cgm,
    detect_agp_patterns,
    TIME_PERIODS,
  )

This file will be removed in a future version.
"""

import warnings

warnings.warn(
    "summary.util.calculate_agp is deprecated. Use summary.features.agp instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Temporary backward compatibility - will be removed
try:
    from summary.features.agp import (
        DEFAULT_TIMEZONE,
        TIME_PERIODS,
        calculate_agp,
        calculate_agp_from_cgm,
        calculate_agp_summary,
        calculate_stats,
        detect_agp_patterns,
        format_agp_json,
    )
except ImportError:
    # Fallback to old location if new structure doesn't exist yet
    from .agp_calculations import calculate_agp, calculate_agp_summary, calculate_stats
    from .agp_config import DEFAULT_TIMEZONE, TIME_PERIODS
    from .agp_formatters import calculate_agp_from_cgm, format_agp_json
    from .agp_patterns import detect_agp_patterns

__all__ = [
    "DEFAULT_TIMEZONE",
    "TIME_PERIODS",
    "calculate_stats",
    "calculate_agp",
    "calculate_agp_summary",
    "format_agp_json",
    "calculate_agp_from_cgm",
    "detect_agp_patterns",
]
