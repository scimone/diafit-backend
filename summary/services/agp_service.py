from summary.models import RollingSummary


def get_agp_summary(user, period_days):
    """Fetch AGP summary for user and period."""
    return RollingSummary.objects.filter(
        user=user, period_days=period_days, agp__isnull=False
    ).first()
