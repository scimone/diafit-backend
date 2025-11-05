# summary/signals.py
from datetime import timedelta

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django_q.models import Schedule


@receiver(post_migrate)
def create_daily_summary_schedule(sender, **kwargs):
    """
    Automatically create a daily schedule for the summary task after migrations.
    """
    func = "summary.tasks.create_daily_summary.create_daily_summary"

    if not Schedule.objects.filter(func=func).exists():
        next_midnight = timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        Schedule.objects.create(
            func=func,
            schedule_type=Schedule.DAILY,
            repeats=-1,
            next_run=next_midnight,
        )
        print(f"✅ Created daily summary schedule (next run: {next_midnight})")
    else:
        print("ℹ️ Daily summary schedule already exists.")
