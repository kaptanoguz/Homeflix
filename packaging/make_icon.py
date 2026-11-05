"""Draws static/icon.svg (a red porthole with a play mark, on a dark rounded square) as PNG/ICO for the desktop packages.

With --web it writes the home screen icons in static/ instead: phones round the corners themselves, so those are
full squares."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 1024
S = SIZE / 64  # icon.svg uses a 64x64 viewBox


def draw(square=False):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=0 if square else 14 * S, fill="#0b0b0f")
    r_out, r_in = (19 + 3.5) * S, (19 - 3.5) * S
    c = 32 * S
    d.ellipse((c - r_out, c - r_out, c + r_out, c + r_out), fill="#e5202e")
    d.ellipse((c - r_in, c - r_in, c + r_in, c + r_in), fill="#0b0b0f")
    for x, y in ((18.57, 18.57), (45.43, 18.57), (18.57, 45.43), (45.43, 45.43)):  # the porthole's bolts
        d.ellipse(((x - 1.8) * S, (y - 1.8) * S, (x + 1.8) * S, (y + 1.8) * S), fill="#0b0b0f")
    d.polygon([(28.5 * S, 23.5 * S), (28.5 * S, 40.5 * S), (41.5 * S, 32 * S)], fill="#e5202e")
    return img


def web_icons():
    static = Path(__file__).resolve().parent.parent / "static"
    icon = draw(square=True).convert("RGB")
    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        icon.resize((size, size), Image.LANCZOS).save(static / name, optimize=True)
    print(f"home screen icons written to {static}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--web"]:
        web_icons()
        sys.exit()
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "build/icons")
    out.mkdir(parents=True, exist_ok=True)
    icon = draw()
    icon.save(out / "lumbuz.png")
    icon.resize((256, 256), Image.LANCZOS).save(out / "lumbuz-256.png")
    icon.save(out / "lumbuz.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"icons written to {out}")
