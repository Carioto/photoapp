from itertools import count
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from gallery.models import Album, Photo


class Command(BaseCommand):
    help = "Import derived photos (web + thumbs) into a new album."

    def add_arguments(self, parser):
        parser.add_argument("--title", required=True, help="Album title")
        parser.add_argument("--web-dir", required=True, help="Path to Derived/web folder")
        parser.add_argument("--thumb-dir", required=True, help="Path to Derived/thumbs folder")
        parser.add_argument("--base-url", help="Base URL for web and thumbnail images (e.g. https://bucket.r2.dev)",)


    def handle(self, *args, **options):
        title = options["title"]
        web_dir = Path(options["web_dir"])
        thumb_dir = Path(options["thumb_dir"])
        base_url = options.get("base_url")


        if not web_dir.exists():
            raise CommandError(f"web-dir not found: {web_dir}")
        if not thumb_dir.exists():
            raise CommandError(f"thumb-dir not found: {thumb_dir}")

        web_files = sorted(web_dir.glob("*.jpg"))
        if not web_files:
            raise CommandError(f"No .jpg files found in: {web_dir}")

        album = Album.objects.create(title=title)
        created = 0
        pairs = list(zip(web_files, thumb_dir.glob("*.jpg")))
        count = 0
        for wf in web_files:
            count += 1
            if count % 5 == 0 or count == len(pairs):
                print(f"Imported {count}/{len(pairs)}")
            base = wf.stem
            tf = thumb_dir / f"{base}.jpg"
            if not tf.exists():
                self.stdout.write(self.style.WARNING(f"Skipping {wf.name} (missing thumb)"))
                continue

            if base_url:
                image_web = f"{base_url}/web/{wf.name}"
                image_thumb = f"{base_url}/thumbs/{tf.name}"
            else:
                image_web = f"/media/web/{wf.name}"
                image_thumb = f"/media/thumbs/{tf.name}"    
            Photo.objects.create(
                album=album,
                title=base.replace("_", " "),
                image_web=image_web,
                image_thumb=image_thumb,)

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created album '{album.title}' with {created} photos."))
