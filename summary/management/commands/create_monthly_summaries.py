# summary/management/commands/create_monthly_summaries.py

from django.core.management.base import BaseCommand

from summary.tasks import create_monthly_summary


class Command(BaseCommand):
    help = "Create monthly summaries for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Target year (defaults to last complete month)",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="Target month (1-12, defaults to last complete month)",
        )

    def handle(self, *args, **options):
        year = options.get("year")
        month = options.get("month")

        self.stdout.write("Starting monthly summary generation...")
        create_monthly_summary(target_year=year, target_month=month)
        self.stdout.write(
            self.style.SUCCESS("Monthly summary generation completed successfully!")
        )
