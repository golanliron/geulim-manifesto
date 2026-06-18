from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "brand" / "print"
OUT.mkdir(parents=True, exist_ok=True)

PDF = OUT / "geuli-notebook-a5-lined.pdf"
PREVIEW = OUT / "geuli-notebook-a5-preview.png"

# A5 at 300 DPI: 148 x 210 mm
W, H = 1748, 2480
NAVY = (31, 53, 94, 255)
OLIVE = (138, 151, 70, 255)
SAND = (216, 199, 160, 255)
CREAM = (248, 246, 241, 255)
GRAY = (110, 118, 132, 255)
WHITE = (255, 255, 255, 255)

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_SMALL = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 28)
FONT_SMALL_B = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 28)

front_src = OUT / "geuli-folder-a4-print-page1.png"
back_src = OUT / "geuli-folder-a4-print-page8.png"
arch_src = ROOT / "brand" / "experiments" / "gaulim-inspired" / "geuli-uploaded-arch-transparent.png"
arch_mark = Image.open(arch_src).convert("RGBA")
if arch_mark.getbbox():
    arch_mark = arch_mark.crop(arch_mark.getbbox())


def resize_cover(path):
    im = Image.open(path).convert("RGB")
    # Fill A5 without distortion.
    scale = max(W / im.width, H / im.height)
    resized = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - W) // 2
    y = (resized.height - H) // 2
    return resized.crop((x, y, x + W, y + H))


def lined_page(page_num):
    page = Image.new("RGB", (W, H), CREAM)
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(wash)
    d.ellipse((-380, -240, 780, 650), fill=(216, 199, 160, 26))
    d.ellipse((1050, -180, 2150, 760), fill=(138, 151, 70, 18))
    page = Image.alpha_composite(page.convert("RGBA"), wash.filter(ImageFilter.GaussianBlur(95))).convert("RGB")
    d = ImageDraw.Draw(page)

    margin_r = 190
    margin_l = 150
    top = 250
    bottom = 2180
    step = 62

    # Tiny brand markers, kept visual and light so the page stays writable.
    mark = arch_mark.resize((54, int(arch_mark.height * 54 / arch_mark.width)), Image.Resampling.LANCZOS)
    page.paste(mark, (W - margin_r - 54, 78), mark)
    for i, color in enumerate([NAVY, OLIVE, SAND]):
        d.ellipse((margin_l + i * 34, 106, margin_l + i * 34 + 14, 120), fill=color)

    # Writing lines.
    y = top
    while y <= bottom:
        d.line((margin_l, y, W - margin_r, y), fill=(31, 53, 94, 70), width=2)
        y += step

    # Subtle side guide and page number.
    d.line((W - 118, top - 25, W - 118, bottom + 20), fill=(216, 199, 160), width=3)
    for i, color in enumerate([NAVY, OLIVE, SAND]):
        d.ellipse((W // 2 - 40 + i * 40, H - 132, W // 2 - 25 + i * 40, H - 117), fill=color)
    d.text((W // 2, H - 78), str(page_num), font=FONT_SMALL, fill=GRAY, anchor="mm")
    return page


pages = [resize_cover(front_src)]
for i in range(1, 101):
    pages.append(lined_page(i))
pages.append(resize_cover(back_src))

pages[0].save(PDF, save_all=True, append_images=pages[1:], resolution=300.0)

# Preview sheet: cover, one lined page, back cover.
thumbs = []
for label, im in [("כריכה", pages[0]), ("עמוד שורות", pages[1]), ("כריכה אחורית", pages[-1])]:
    tw = 360
    th = int(im.height * tw / im.width)
    thumb = im.resize((tw, th), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th + 42), WHITE)
    canvas.paste(thumb, (0, 42))
    d = ImageDraw.Draw(canvas)
    d.text((tw // 2, 20), label, font=FONT_SMALL_B, fill=NAVY, anchor="mm")
    thumbs.append(canvas)

gap = 28
sheet = Image.new("RGB", (3 * thumbs[0].width + 4 * gap, thumbs[0].height + 2 * gap), (245, 244, 240))
for i, t in enumerate(thumbs):
    sheet.paste(t, (gap + i * (t.width + gap), gap))
sheet.save(PREVIEW, quality=95)

print(PDF.resolve())
print(PREVIEW.resolve())
