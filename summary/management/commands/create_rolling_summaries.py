# summary/management/commands/create_rolling_summaries.py

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from summary.tasks import create_rolling_summary


class Command(BaseCommand):
    help = "Create rolling summaries for all users (1, 3, 7, 14, 30, 90 days)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--periods",
            nargs="+",
            type=int,
            default=[1, 3, 7, 14, 30, 90],
            help="Rolling periods in days (default: 1 3 7 14 30 90)",
        )
        parser.add_argument(
            "--end-date",
            type=str,
            help="End date for rolling periods in YYYY-MM-DD format (defaults to today)",
        )

    def handle(self, *args, **options):
        periods = options.get("periods")
        end_date_str = options.get("end_date")
        
        end_date = None
        if end_date_str:
            end_date = parse_date(end_date_str)
            if not end_date:
                self.stdout.write(
                    self.style.ERROR(f"Invalid date format: {end_date_str}. Use YYYY-MM-DD.")
                )
                return
        
        self.stdout.write(f"Starting rolling summary generation for periods: {periods}")
        if end_date:
            self.stdout.write(f"End date: {end_date}")
        
        create_rolling_summary(period_days_list=periods, end_date=end_date)
        self.stdout.write(
            self.style.SUCCESS("Rolling summary generation completed successfully!")
        )