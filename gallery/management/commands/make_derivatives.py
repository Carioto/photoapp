from __future__ import annotations

from pathlib import Path
from shutil import copy2
from PIL import Image, ImageOps

# ----- Settings you can tweak -----
WEB_MAX_W = 1600
THUMB_MAX_W = 400
JPEG_QUALITY = 85

SUPPORTED_INPUT_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

BATCH_NAME = "batch_007"  # Change this for each new batch


def save_jpeg_resized(src_path: Path, dst_path: Path, max_width: int) -> None:
    """
    Open image, normalize orientation, convert to RGB,
    resize to max_width preserving aspect ratio (never upscale),
    and save as JPEG.
    """
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)

        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        w, h = im.size

        if w > max_width:
            new_w = max_width
            new_h = round(h * (new_w / w))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        im.save(
            dst_path,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )


def copy_original_to_web(src_path: Path, dst_path: Path) -> None:
    """
    Copy JPG/JPEG originals directly to web output to avoid any extra JPEG recompression.
    """
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(src_path, dst_path)


def main() -> None:
    # CHANGE THESE PATHS to match your machine/NAS mapping
    input_dir = Path(rf"Z:\FamilyPhotos\Originals\{BATCH_NAME}")
    out_web_dir = Path(r"Z:\FamilyPhotos\Derived\web")
    out_thumb_dir = Path(r"Z:\FamilyPhotos\Derived\thumbs")

    if not input_dir.exists():
        raise SystemExit(f"Input folder not found: {input_dir}")

    files = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_INPUT_EXTS
    ]
    files.sort()

    if not files:
        raise SystemExit(f"No images found in: {input_dir}")

    print(f"Found {len(files)} images in {input_dir}")

    for i, src in enumerate(files, start=1):
        base_name = src.stem
        ext = src.suffix.lower()

        web_out = out_web_dir / f"{base_name}.jpg"
        thumb_out = out_thumb_dir / f"{base_name}.jpg"

        try:
            if ext in {".jpg", ".jpeg"}:
                # Web: copy original JPG bytes (no re-encode)
                copy_original_to_web(src, web_out)
                # Thumbs: generate resized JPEG (single re-encode)
                save_jpeg_resized(src, thumb_out, THUMB_MAX_W)
                print(f"[{i:03}] OK  {src.name} -> web(COPY) + thumb(ENCODE)")
            else:
                # Non-JPG: generate web + thumb JPEGs from source (same as before)
                save_jpeg_resized(src, web_out, WEB_MAX_W)
                save_jpeg_resized(src, thumb_out, THUMB_MAX_W)
                print(f"[{i:03}] OK  {src.name} -> web + thumb")
        except Exception as e:
            print(f"[{i:03}] FAIL {src.name}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
