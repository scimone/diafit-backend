# summary/management/commands/create_weekly_summaries.py

from django.core.management.base import BaseCommand

from summary.tasks import create_weekly_summary


class Command(BaseCommand):
    help = "Create weekly summaries for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Target year (defaults to last complete week)",
        )
        parser.add_argument(
            "--week",
            type=int,
            help="Target week number (1-53, defaults to last complete week)",
        )

    def handle(self, *args, **options):
        year = options.get("year")
        week = options.get("week")

        self.stdout.write("Starting weekly summary generation...")
        create_weekly_summary(target_year=year, target_week=week)
        self.stdout.write(
            self.style.SUCCESS("Weekly summary generation completed successfully!")
        )
