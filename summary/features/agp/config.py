"""
AGP Configuration Constants
All thresholds and time windows for AGP calculations and pattern detection.
"""

import pytz

# Default timezone for users
DEFAULT_TIMEZONE = pytz.timezone("Europe/Berlin")

# Shared time period definitions (in hours)
TIME_PERIODS = {
    "night": (22, 7),  # 22:00 - 07:00 (wraps around midnight)
    "morning": (7, 11),  # 07:00 - 11:00
    "noon": (11, 15),  # 11:00 - 15:00
    "afternoon": (15, 18),  # 15:00 - 18:00
    "evening": (18, 22),  # 18:00 - 22:00
}

# Time configuration
POINTS_PER_HOUR = 12  # 5-min intervals: 60/5 = 12 points per hour
POINTS_PER_DAY = 288  # 24 hours * 12 points/hour

# Clinical glucose thresholds (mg/dL)
HYPO_THRESHOLD = 70  # Hypoglycemia threshold
SEVERE_HYPO_THRESHOLD = 54  # Severe hypoglycemia threshold
TARGET_LOW = 70  # General target range low
TARGET_HIGH = 180  # General target range high
VERY_HIGH = 250  # Very high glucose threshold
OPTIMAL_LOW = 70  # Optimal range low
OPTIMAL_HIGH = 140  # Optimal range high

# Fasting glucose thresholds (mg/dL)
FASTING_OPTIMAL_LOW = 70
FASTING_OPTIMAL_HIGH = 100  # Stricter for fasting
FASTING_TARGET_HIGH = 130  # Maximum acceptable fasting

# Variability thresholds (mg/dL)
WIDE_IQR = 60  # High daily variability threshold
TIGHT_IQR = 30  # Tight control threshold
CONSISTENCY_THRESHOLD = 100  # Outer band threshold for consistency
CONSISTENT_OUTER_BAND = 40  # Very narrow outer band

# Meal spike thresholds
MEAL_SPIKE_THRESHOLD = 50  # mg/dL rise for meal spike detection

# Dawn phenomenon
DAWN_START_HOUR = 3  # Start of dawn phenomenon window
DAWN_END_HOUR = 7  # End of dawn phenomenon window
DAWN_RISE_THRESHOLD = 20  # mg/dL rise to detect dawn phenomenon

# Somogyi effect
SOMOGYI_NIGHT_START_HOUR = 2  # Early night low check start
SOMOGYI_NIGHT_END_HOUR = 4  # Early night low check end
SOMOGYI_MORNING_START_HOUR = 6  # Morning rebound check start
SOMOGYI_MORNING_END_HOUR = 8  # Morning rebound check end

# Fasting glucose window
FASTING_START_HOUR = 5  # Fasting glucose window start
FASTING_END_HOUR = 7  # Fasting glucose window end

# Meal timing windows (hours)
BREAKFAST_PRE_HOUR = 6
BREAKFAST_START_HOUR = 7
BREAKFAST_END_HOUR = 10

LUNCH_PRE_HOUR = 11
LUNCH_START_HOUR = 12
LUNCH_END_HOUR = 15

DINNER_PRE_HOUR = 18
DINNER_START_HOUR = 19
DINNER_END_HOUR = 22

# Meal response quality thresholds
RAPID_SPIKE_TIME_THRESHOLD = 30  # minutes - rapid spike if peak <30 min
RAPID_SPIKE_RISE_THRESHOLD = 50  # mg/dL - rapid spike if rise >50
PROLONGED_ELEVATION_DURATION = 90  # minutes - prolonged if elevated >90 min
ELEVATION_THRESHOLD_OFFSET = 30  # mg/dL above baseline to consider "elevated"
RECOVERY_THRESHOLD = 20  # mg/dL from baseline to consider "recovered"
RECOVERY_THRESHOLD_DELAYED = 30  # mg/dL from baseline for delayed recovery

# Good meal response criteria
GOOD_MEAL_RISE_MIN = 20  # mg/dL minimum rise
GOOD_MEAL_RISE_MAX = 40  # mg/dL maximum rise
GOOD_MEAL_PEAK_TIME_MIN = 30  # minutes minimum time to peak
GOOD_MEAL_PEAK_TIME_MAX = 90  # minutes maximum time to peak

# Consistency check windows
MORNING_CONSISTENCY_START_HOUR = 7
MORNING_CONSISTENCY_END_HOUR = 9
BEDTIME_CONSISTENCY_START_HOUR = 21
BEDTIME_CONSISTENCY_END_HOUR = 23
INCONSISTENT_MORNING_THRESHOLD = 100  # mg/dL outer band
INCONSISTENT_BEDTIME_THRESHOLD = 100  # mg/dL outer band

# Overnight stability
STABLE_NIGHT_IQR = 25  # mg/dL - stable if IQR < 25
FLUCTUATING_NIGHT_IQR = 50  # mg/dL - fluctuating if IQR > 50
