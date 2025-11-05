# summary/management/commands/create_quarterly_summaries.py

from django.core.management.base import BaseCommand

from summary.tasks import create_quarterly_summary


class Command(BaseCommand):
    help = "Create quarterly summaries for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Target year (defaults to last complete quarter)",
        )
        parser.add_argument(
            "--quarter",
            type=int,
            choices=[1, 2, 3, 4],
            help="Target quarter (1-4, defaults to last complete quarter)",
        )

    def handle(self, *args, **options):
        year = options.get("year")
        quarter = options.get("quarter")

        self.stdout.write("Starting quarterly summary generation...")
        create_quarterly_summary(target_year=year, target_quarter=quarter)
        self.stdout.write(
            self.style.SUCCESS("Quarterly summary generation completed successfully!")
        )
