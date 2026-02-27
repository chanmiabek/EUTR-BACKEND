from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Q
from PIL import Image

from applications.models import TeamMember
from volunteering.models import Opportunity


class Command(BaseCommand):
    help = "Backfill default images for TeamMember and Opportunity records with missing images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without writing changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        media_root = Path(settings.MEDIA_ROOT)
        defaults_dir = media_root / "defaults"
        team_default_path = defaults_dir / "team-default.png"
        volunteer_default_path = defaults_dir / "volunteer-default.png"

        self._ensure_default_image(team_default_path, color=(37, 99, 235))
        self._ensure_default_image(volunteer_default_path, color=(22, 163, 74))

        team_default_url = f"{settings.MEDIA_URL.rstrip('/')}/defaults/team-default.png"

        team_qs = TeamMember.objects.filter(
            Q(photo__isnull=True) | Q(photo=""),
            Q(image__isnull=True) | Q(image=""),
        )
        opp_qs = Opportunity.objects.filter(Q(image__isnull=True) | Q(image=""))

        team_count = team_qs.count()
        opp_count = opp_qs.count()

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run mode; no records updated."))
            self.stdout.write(f"Team members to update: {team_count}")
            self.stdout.write(f"Volunteer opportunities to update: {opp_count}")
            return

        team_updated = team_qs.update(image=team_default_url)

        opp_updated = 0
        for opp in opp_qs:
            with volunteer_default_path.open("rb") as img_file:
                opp.image.save(f"opportunity-default-{opp.pk}.png", File(img_file), save=True)
            opp_updated += 1

        self.stdout.write(self.style.SUCCESS("Default image backfill completed."))
        self.stdout.write(f"Team members updated: {team_updated}")
        self.stdout.write(f"Volunteer opportunities updated: {opp_updated}")

    def _ensure_default_image(self, path: Path, color):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return
        image = Image.new("RGB", (1200, 800), color)
        image.save(path, format="PNG")
