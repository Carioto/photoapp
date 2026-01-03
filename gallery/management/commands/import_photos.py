from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from gallery.models import Album, Photo


class Command(BaseCommand):
    help = "Import derived photos (web + thumbs) into a new album."

    def add_arguments(self, parser):
        parser.add_argument("--title", required=True, help="Album title")
        parser.add_argument("--web-dir", required=True, help="Path to Derived/web folder")
        parser.add_argument("--thumb-dir", required=True, help="Path to Derived/thumbs folder")

    def handle(self, *args, **options):
        title = options["title"]
        web_dir = Path(options["web_dir"])
        thumb_dir = Path(options["thumb_dir"])

        if not web_dir.exists():
            raise CommandError(f"web-dir not found: {web_dir}")
        if not thumb_dir.exists():
            raise CommandError(f"thumb-dir not found: {thumb_dir}")

        web_files = sorted(web_dir.glob("*.jpg"))
        if not web_files:
            raise CommandError(f"No .jpg files found in: {web_dir}")

        album = Album.objects.create(title=title)
        created = 0

        for wf in web_files:
            base = wf.stem
            tf = thumb_dir / f"{base}.jpg"
            if not tf.exists():
                self.stdout.write(self.style.WARNING(f"Skipping {wf.name} (missing thumb)"))
                continue

            # Store as paths for now. Later you'll store R2 URLs.
            Photo.objects.create(
                album=album,
                title=base.replace("_", " "),
                image_web=f"/media/web/{wf.name}",
                image_thumb=f"/media/thumbs/{tf.name}",
)

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created album '{album.title}' with {created} photos."))
