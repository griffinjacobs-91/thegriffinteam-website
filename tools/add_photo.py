#!/usr/bin/env python3
"""Get a photo ready for the website.
Usage: python3 tools/add_photo.py <photo file> <new name> [folder]
Example: python3 tools/add_photo.py inbox/IMG_2041.HEIC 2041-k-road-front sold
Saves site/assets/<folder>/<new name>.jpg at most 1600 px wide, turned the right way up,
compressed for the web, and with location and camera details removed (privacy).
Prints the width and height to put in the page."""
import sys, pathlib
try:
    from PIL import Image, ImageOps
except ImportError:
    raise SystemExit("Needs Pillow: run  pip install pillow  (and  pip install pillow-heif  for iPhone HEIC photos)")
try:
    from pillow_heif import register_heif_opener; register_heif_opener()
except ImportError:
    pass
if len(sys.argv) < 3: raise SystemExit(__doc__)
src, name = pathlib.Path(sys.argv[1]), sys.argv[2]
folder = sys.argv[3] if len(sys.argv) > 3 else ""
root = pathlib.Path(__file__).resolve().parent.parent
out = root / "site" / "assets" / folder / f"{name}.jpg"
out.parent.mkdir(parents=True, exist_ok=True)
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
im.save(out, "JPEG", quality=80, optimize=True, progressive=True)  # no exif passed, so GPS is dropped
print(f"{out.relative_to(root / 'site')}  {im.width}x{im.height}  {out.stat().st_size // 1024} KB")
