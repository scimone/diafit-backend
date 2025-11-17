from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.colors import COLORS


class Command(BaseCommand):
    help = "Generate CSS variables from COLOR_SCHEMES and write to static files."

    def handle(self, *args, **options):
        css_lines = [":root {"]

        for group, colors in COLORS.items():
            for key, value in colors.items():
                css_var = (
                    f"--{group.replace('_', '-')}-{key.replace('_', '-')}: {value};"
                )
                css_lines.append(f"    {css_var}")

        css_lines.append("}")

        output_file = (
            Path(settings.BASE_DIR) / "core" / "static" / "core" / "css" / "colors.css"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(css_lines))

        self.stdout.write(
            self.style.SUCCESS(f"[sync_colors] Wrote CSS variables to {output_file}")
        )
