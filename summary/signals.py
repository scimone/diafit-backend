# summary/signals.py
from datetime import timedelta

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django_q.models import Schedule


@receiver(post_migrate)
def create_summary_schedules(sender, **kwargs):
    """
    Automatically create schedules for all summary tasks after migrations.
    """
    now = timezone.now()

    # Daily summary - runs daily at midnight
    daily_func = "summary.tasks.create_daily_summary.create_daily_summary"
    if not Schedule.objects.filter(func=daily_func).exists():
        next_midnight = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        Schedule.objects.create(
            func=daily_func,
            schedule_type=Schedule.DAILY,
            repeats=-1,
            next_run=next_midnight,
        )
        print(f"✅ Created daily summary schedule (next run: {next_midnight})")
    else:
        print("ℹ️ Daily summary schedule already exists.")

    # Weekly summary - runs every Monday at 1 AM
    weekly_func = "summary.tasks.create_weekly_summary.create_weekly_summary"
    if not Schedule.objects.filter(func=weekly_func).exists():
        # Calculate next Monday at 1 AM
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 1:  # If it's Monday and after 1 AM
            days_until_monday = 7
        next_monday = (now + timedelta(days=days_until_monday)).replace(
            hour=1, minute=0, second=0, microsecond=0
        )

        Schedule.objects.create(
            func=weekly_func,
            schedule_type=Schedule.WEEKLY,
            repeats=-1,
            next_run=next_monday,
        )
        print(f"✅ Created weekly summary schedule (next run: {next_monday})")
    else:
        print("ℹ️ Weekly summary schedule already exists.")

    # Monthly summary - runs on the 1st of each month at 2 AM
    monthly_func = "summary.tasks.create_monthly_summary.create_monthly_summary"
    if not Schedule.objects.filter(func=monthly_func).exists():
        # Calculate next 1st of month at 2 AM
        if now.day == 1 and now.hour < 2:
            next_first = now.replace(hour=2, minute=0, second=0, microsecond=0)
        else:
            if now.month == 12:
                next_first = now.replace(
                    year=now.year + 1,
                    month=1,
                    day=1,
                    hour=2,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            else:
                next_first = now.replace(
                    month=now.month + 1,
                    day=1,
                    hour=2,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

        Schedule.objects.create(
            func=monthly_func,
            schedule_type=Schedule.MONTHLY,
            repeats=-1,
            next_run=next_first,
        )
        print(f"✅ Created monthly summary schedule (next run: {next_first})")
    else:
        print("ℹ️ Monthly summary schedule already exists.")

    # Quarterly summary - runs on the 1st of Jan, Apr, Jul, Oct at 3 AM
    quarterly_func = "summary.tasks.create_quarterly_summary.create_quarterly_summary"
    if not Schedule.objects.filter(func=quarterly_func).exists():
        # Calculate next quarter start at 3 AM
        quarter_months = [1, 4, 7, 10]
        next_quarter_month = None

        for month in quarter_months:
            if now.month <= month:
                if now.month == month and now.day == 1 and now.hour < 3:
                    next_quarter_month = month
                    break
                elif now.month < month:
                    next_quarter_month = month
                    break

        if next_quarter_month is None:  # Next quarter is in next year
            next_quarter_month = 1
            next_quarter_year = now.year + 1
        else:
            next_quarter_year = now.year

        next_quarter = now.replace(
            year=next_quarter_year,
            month=next_quarter_month,
            day=1,
            hour=3,
            minute=0,
            second=0,
            microsecond=0,
        )

        Schedule.objects.create(
            func=quarterly_func,
            schedule_type=Schedule.QUARTERLY,
            repeats=-1,
            next_run=next_quarter,
        )
        print(f"✅ Created quarterly summary schedule (next run: {next_quarter})")
    else:
        print("ℹ️ Quarterly summary schedule already exists.")

    # Rolling summary - runs every hour
    rolling_func = "summary.tasks.create_rolling_summary.create_rolling_summary"
    if not Schedule.objects.filter(func=rolling_func).exists():
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        Schedule.objects.create(
            func=rolling_func,
            schedule_type=Schedule.HOURLY,
            repeats=-1,
            next_run=next_hour,
        )
        print(f"✅ Created rolling summary schedule (next run: {next_hour})")
    else:
        print("ℹ️ Rolling summary schedule already exists.")
