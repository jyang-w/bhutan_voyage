"""place_images.py - one place to get a picture for a destination.

Real photo      images/<name in catalog>  - or, if the catalog has none, images/<key>.jpg|jpeg|png|webp
                (so adding a photo is just: save the file as the place's key, e.g. images/rinpung-dzong.jpg).
No photo yet    a neutral "Photo coming soon" card is drawn instead, with the place name on it.

Everything here returns plain PIL images, so the pages can wrap them with ImageTk as usual.
"""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

IMAGE_DIR = Path(__file__).resolve().parent / "images"
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# neutral, warm greys - it should read as "empty", not as a broken image
_BG_TOP = (236, 232, 224)
_BG_BOTTOM = (222, 217, 208)
_RIDGE_BACK = (212, 206, 196)
_RIDGE_FRONT = (201, 195, 184)
_TEXT = (110, 102, 92)
_TEXT_SOFT = (150, 142, 131)


def photo_path(d):
    """Path of this place's photo, or None if it has none yet."""
    if d.get("image"):
        p = IMAGE_DIR / d["image"]
        if p.exists():
            return p
    for ext in EXTENSIONS:
        p = IMAGE_DIR / f"{d['key']}{ext}"
        if p.exists():
            return p
    return None


def has_photo(d):
    return photo_path(d) is not None


def _font(px, bold=False):
    names = (("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf") if bold
             else ("DejaVuSans.ttf", "Arial.ttf", "arial.ttf"))
    for name in names:
        try:
            return ImageFont.truetype(name, px)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def placeholder(d, width, height):
    """The "photo coming soon" card for a place."""
    width, height = max(40, int(width)), max(30, int(height))
    img = Image.new("RGB", (width, height), _BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(height):                         # soft vertical gradient
        t = y / max(1, height - 1)
        draw.line([(0, y), (width, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(_BG_TOP, _BG_BOTTOM)))
    # two quiet mountain ridges along the bottom
    draw.polygon([(0, height), (0, height * 0.72), (width * 0.22, height * 0.5), (width * 0.38, height * 0.66),
                  (width * 0.62, height * 0.42), (width * 0.85, height * 0.64), (width, height * 0.55),
                  (width, height)], fill=_RIDGE_BACK)
    draw.polygon([(0, height), (0, height * 0.86), (width * 0.3, height * 0.72), (width * 0.55, height * 0.86),
                  (width * 0.8, height * 0.74), (width, height * 0.84), (width, height)], fill=_RIDGE_FRONT)

    title_px = max(11, int(height * 0.115))
    small_px = max(9, int(height * 0.068))
    title_font, small_font = _font(title_px, bold=True), _font(small_px)
    lines = _wrap(draw, d["title"], title_font, width * 0.82)[:3]
    line_h = int(title_px * 1.25)
    block_h = line_h * len(lines) + int(small_px * 2.6)
    y = max(6, (height * 0.62 - block_h) / 2)
    for line in lines:
        w = draw.textlength(line, font=title_font)
        draw.text(((width - w) / 2, y), line, font=title_font, fill=_TEXT)
        y += line_h
    for text in (d.get("dzongkhag", ""), "Photo coming soon"):
        if text:
            w = draw.textlength(text, font=small_font)
            draw.text(((width - w) / 2, y + small_px * 0.3), text, font=small_font, fill=_TEXT_SOFT)
            y += int(small_px * 1.4)
    return img


@lru_cache(maxsize=32)
def _open_rgb(path_str):
    """The photo as RGB, shrunk to at most 1600 px wide (some originals are several MB)."""
    with Image.open(path_str) as source:
        if source.mode in ("RGBA", "P", "LA"):
            source = source.convert("RGBA")
            bg = Image.new("RGB", source.size, (255, 255, 255))
            bg.paste(source, mask=source.split()[-1])
            image = bg
        else:
            image = source.convert("RGB")
    if image.width > 1600:
        image = image.resize((1600, int(image.height * 1600 / image.width)), Image.Resampling.LANCZOS)
    return image


def load(d, width, height):
    """A (width x height) picture for the place: its photo cropped to fit, or the placeholder."""
    p = photo_path(d)
    if p is not None:
        try:
            return ImageOps.fit(_open_rgb(str(p)), (int(width), int(height)), method=Image.Resampling.LANCZOS)
        except Exception as exc:                      # unreadable file: fall back rather than crash the page
            print(f"[image error] {p.name}: {exc}")
    return placeholder(d, width, height)
