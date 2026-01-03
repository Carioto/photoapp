from pathlib import Path
import csv

base = Path(r"Z:\FamilyPhotos")
web_dir = base / "Derived" / "web"
thumb_dir = base / "Derived" / "thumbs"
out_csv = base / "Derived" / "manifest.csv"

web_files = sorted(web_dir.glob("*.jpg"))

with out_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["base_name", "web_file", "thumb_file", "year", "title", "notes"])
    for wf in web_files:
        base_name = wf.stem
        tf = thumb_dir / f"{base_name}.jpg"
        w.writerow([base_name, str(wf), str(tf), "", "", ""])

print(f"Wrote: {out_csv}")
