# summary/management/commands/create_all_summaries.py

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from summary.tasks import (
    create_daily_summary,
    create_monthly_summary,
    create_quarterly_summary,
    create_rolling_summary,
    create_weekly_summary,
)


class Command(BaseCommand):
    help = "Create all types of summaries for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--types",
            nargs="+",
            choices=["daily", "weekly", "monthly", "quarterly", "rolling"],
            default=["daily", "weekly", "monthly", "quarterly", "rolling"],
            help="Summary types to generate (default: all types)",
        )
        parser.add_argument(
            "--date",
            type=str,
            help="Target date in YYYY-MM-DD format (for daily summary)",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="Target year (for weekly/monthly/quarterly summaries)",
        )
        parser.add_argument(
            "--week",
            type=int,
            help="Target week number (1-53, for weekly summary)",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="Target month (1-12, for monthly summary)",
        )
        parser.add_argument(
            "--quarter",
            type=int,
            choices=[1, 2, 3, 4],
            help="Target quarter (1-4, for quarterly summary)",
        )
        parser.add_argument(
            "--rolling-periods",
            nargs="+",
            type=int,
            default=[1, 3, 7, 14, 30, 90],
            help="Rolling periods in days (default: 1 3 7 14 30 90)",
        )

    def handle(self, *args, **options):
        summary_types = options.get("types")
        target_date = options.get("date")
        year = options.get("year")
        week = options.get("week")
        month = options.get("month")
        quarter = options.get("quarter")
        rolling_periods = options.get("rolling_periods")

        # Parse date if provided
        parsed_date = None
        if target_date:
            parsed_date = parse_date(target_date)
            if not parsed_date:
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid date format: {target_date}. Use YYYY-MM-DD."
                    )
                )
                return

        self.stdout.write(
            f"Starting summary generation for types: {', '.join(summary_types)}"
        )

        # Daily summary
        if "daily" in summary_types:
            self.stdout.write("📆 Generating daily summaries...")
            create_daily_summary(target_date=parsed_date)

        # Weekly summary
        if "weekly" in summary_types:
            self.stdout.write("📅 Generating weekly summaries...")
            create_weekly_summary(target_year=year, target_week=week)

        # Monthly summary
        if "monthly" in summary_types:
            self.stdout.write("📅 Generating monthly summaries...")
            create_monthly_summary(target_year=year, target_month=month)

        # Quarterly summary
        if "quarterly" in summary_types:
            self.stdout.write("📅 Generating quarterly summaries...")
            create_quarterly_summary(target_year=year, target_quarter=quarter)

        # Rolling summary
        if "rolling" in summary_types:
            self.stdout.write("📊 Generating rolling summaries...")
            end_date = None
            if parsed_date:
                from datetime import datetime, timezone

                end_date = datetime.combine(parsed_date, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
            create_rolling_summary(period_days_list=rolling_periods, end_date=end_date)

        self.stdout.write(
            self.style.SUCCESS("All summary generation completed successfully!")
        )
