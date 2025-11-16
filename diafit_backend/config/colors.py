# diafit_backend/config/colors.py

COLOR_SCHEMES = {
    "diafit": {
        "in_range": "rgba(140, 237, 194, 1)",
        "above_range": "rgba(168, 130, 255, 1)",
        "under_range": "rgba(255, 105, 97, 1)",
    },
    "agp": {
        "in_range_median": "rgba(67, 217, 152, 1)",
        "in_range_75th": "rgba(67, 217, 152, 0.55)",
        "in_range_90th": "rgba(67, 217, 152, 0.25)",
        "above_range_75th": "rgba(168, 130, 255, 0.45)",
        "above_range_90th": "rgba(168, 130, 255, 0.25)",
        "under_range_75th": "rgba(255, 105, 97, 0.55)",
        "under_range_90th": "rgba(255, 105, 97, 0.25)",
        "target_upper_line": "rgba(168, 130, 255, 0.7)",
        "target_lower_line": "rgba(255, 105, 97, 0.7)",
    },
}
