# summary/management/commands/backfill_summaries.py
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand

from summary.tasks.create_daily_summary import create_daily_summary


class Command(BaseCommand):
    help = "Backfill daily summaries for a given date range."

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            type=str,
            required=True,
            help="Start date (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--end",
            type=str,
            required=False,
            help="End date (YYYY-MM-DD). Defaults to yesterday.",
        )

    def handle(self, *args, **options):
        start_str = options["start"]
        end_str = options.get("end")

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            if end_str:
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            else:
                end_date = date.today() - timedelta(days=1)
        except ValueError:
            self.stderr.write(
                self.style.ERROR("❌ Invalid date format. Use YYYY-MM-DD.")
            )
            return

        if end_date < start_date:
            self.stderr.write(self.style.ERROR("❌ End date must be >= start date."))
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"📊 Backfilling summaries from {start_date} to {end_date}..."
            )
        )

        total_days = (end_date - start_date).days + 1
        for i in range(total_days):
            target_day = start_date + timedelta(days=i)
            create_daily_summary(target_day)

        self.stdout.write(self.style.SUCCESS("✅ Backfill complete."))
