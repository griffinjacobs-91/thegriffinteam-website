#!/usr/bin/env python3
"""Get a photo ready for the website.
Usage: python3 tools/add_photo.py <photo file> <new name> [folder]
Example: python3 tools/add_photo.py inbox/IMG_2041.HEIC 2041-k-road-front sold
Saves two copies, turned the right way up, compressed for the web, and with location and
camera details removed (privacy):
  site/assets/<folder>/<new name>.jpg     sharp enough for big screens (up to 2560 px wide,
                                          1800 px for a tall photo)
  site/assets/<folder>/<new name>-sm.jpg  1200 px wide, which phones load instead
The site picks the right copy by itself. Start from the full-size original, never a
screenshot or a photo saved from a text message: small photos look soft on big screens.
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
def save(img, path, maxw):
    if img.width > maxw: img = img.resize((maxw, round(img.height * maxw / img.width)), Image.LANCZOS)
    img.save(path, "JPEG", quality=80, optimize=True, progressive=True)  # no exif passed, so GPS is dropped
    return img
big = save(im, out, 2560 if im.width >= im.height else 1800)
save(im, out.with_name(f"{name}-sm.jpg"), 1200)
if big.width < 1800: print("Note: this photo is small. It will look soft as a wide banner; use it in a card or ask for the original.")
print(f"{out.relative_to(root / 'site')}  {big.width}x{big.height}  {out.stat().st_size // 1024} KB")
