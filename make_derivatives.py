from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps

# ----- Settings you can tweak -----
WEB_MAX_W = 1600
THUMB_MAX_W = 400
JPEG_QUALITY = 85

# If you want: keep filenames but change extension to .jpg
SUPPORTED_INPUT_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


def save_jpeg_resized(src_path: Path, dst_path: Path, max_width: int) -> None:
    """
    Open image, normalize orientation, convert to RGB,
    resize to max_width preserving aspect ratio (never upscale),
    and save as JPEG.
    """
    with Image.open(src_path) as im:
        # Fix rotated images if EXIF orientation exists (common for phone pics)
        im = ImageOps.exif_transpose(im)

        # Convert to RGB for JPEG (PNG/TIFF may be RGBA or palette)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif im.mode == "L":
            # grayscale is fine; JPEG supports it
            pass

        w, h = im.size

        # Don't upscale small images
        if w > max_width:
            new_w = max_width
            new_h = round(h * (new_w / w))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # optimize + progressive helps with web loading
        im.save(
            dst_path,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )


def main() -> None:
    # CHANGE THESE PATHS to match your machine/NAS mapping
    input_dir = Path(r"Z:\FamilyPhotos\Originals\batch_001")  # <-- your NAS mapped drive path
    out_web_dir = Path(r"Z:\FamilyPhotos\Derived\web")
    out_thumb_dir = Path(r"Z:\FamilyPhotos\Derived\thumbs")

    if not input_dir.exists():
        raise SystemExit(f"Input folder not found: {input_dir}")

    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_INPUT_EXTS]
    files.sort()

    if not files:
        raise SystemExit(f"No images found in: {input_dir}")

    print(f"Found {len(files)} images in {input_dir}")

    for i, src in enumerate(files, start=1):
        base_name = src.stem  # filename without extension

        web_out = out_web_dir / f"{base_name}.jpg"
        thumb_out = out_thumb_dir / f"{base_name}.jpg"

        try:
            save_jpeg_resized(src, web_out, WEB_MAX_W)
            save_jpeg_resized(src, thumb_out, THUMB_MAX_W)
            print(f"[{i:03}] OK  {src.name} -> web + thumb")
        except Exception as e:
            print(f"[{i:03}] FAIL {src.name}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
