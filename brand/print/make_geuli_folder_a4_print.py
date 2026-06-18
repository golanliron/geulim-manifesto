from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "brand" / "print"
OUT.mkdir(parents=True, exist_ok=True)

PDF = OUT / "geuli-folder-a4-print.pdf"
PREVIEWS = [OUT / f"geuli-folder-a4-print-page{i}.png" for i in range(1, 9)]

W, H = 2480, 3508
NAVY = (31, 53, 94, 255)
DEEP = (15, 27, 51, 255)
OLIVE = (138, 151, 70, 255)
SAND = (216, 199, 160, 255)
CREAM = (248, 246, 241, 255)
WHITE = (255, 255, 255, 255)
GRAY = (88, 98, 116, 255)
LIGHT = (255, 255, 255, 238)

FONT_DIR = Path(r"C:\Windows\Fonts")
font_hero = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 142)
font_title = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 94)
font_h = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 58)
font_body = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 40)
font_body_b = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 40)
font_small = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 30)
font_small_b = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 30)
font_tiny = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 24)
font_word_big = ImageFont.truetype(str(FONT_DIR / "FRANKB.TTF"), 130)
font_word = ImageFont.truetype(str(FONT_DIR / "FRANKB.TTF"), 76)

arch = Image.open(ROOT / "brand" / "experiments" / "gaulim-inspired" / "geuli-uploaded-arch-transparent.png").convert("RGBA")
city = Image.open(ROOT / "brand" / "experiments" / "gaulim-inspired" / "geuli-landscape-strip-transparent.png").convert("RGBA")
if arch.getbbox():
    arch = arch.crop(arch.getbbox())


def rtl_text(draw, x, y, text, font, fill, anchor="mm"):
    try:
        draw.text((x, y), text, font=font, fill=fill, anchor=anchor, direction="rtl")
    except Exception:
        draw.text((x, y), text[::-1], font=font, fill=fill, anchor=anchor)


def text_width(draw, text, font):
    try:
        box = draw.textbbox((0, 0), text, font=font, direction="rtl")
    except Exception:
        box = draw.textbbox((0, 0), text[::-1], font=font)
    return box[2] - box[0]


def wrap(draw, text, font, width):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        test = word if not cur else cur + " " + word
        if text_width(draw, test, font) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def multiline(draw, x, y, text, font, fill, width, gap=12, center=True):
    yy = y
    for para in text.split("\n"):
        for line in wrap(draw, para, font, width):
            box = draw.textbbox((0, 0), line, font=font)
            h = box[3] - box[1]
            if center:
                rtl_text(draw, x, yy + h / 2, line, font, fill)
            else:
                rtl_text(draw, x, yy, line, font, fill, "ra")
            yy += h + gap
        yy += gap
    return yy


def page_base():
    page = Image.new("RGBA", (W, H), CREAM)
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(wash)
    d.ellipse((-560, -300, 1060, 880), fill=(216, 199, 160, 44))
    d.ellipse((1480, -220, 3040, 890), fill=(138, 151, 70, 30))
    d.ellipse((460, 300, 2140, 1740), fill=(255, 255, 255, 120))
    return Image.alpha_composite(page, wash.filter(ImageFilter.GaussianBlur(120)))


def dots(draw, cx, y, r=13, colors=(NAVY, OLIVE, SAND)):
    for i, color in enumerate(colors):
        x = cx - 44 + i * 44
        draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)


def dot_grid(draw, x, y, cols=6, rows=5, step=48, r=8, alpha=70):
    for row in range(rows):
        for col in range(cols):
            color = [SAND, OLIVE, NAVY][(row + col) % 3]
            fill = (color[0], color[1], color[2], alpha)
            draw.ellipse((x + col * step, y + row * step, x + col * step + 2 * r, y + row * step + 2 * r), fill=fill)


def corner(draw):
    draw.line((170, 280, 170, 520), fill=(216, 199, 160, 180), width=3)
    draw.line((170, 280, 410, 280), fill=(216, 199, 160, 180), width=3)
    draw.line((W - 170, H - 280, W - 170, H - 520), fill=(216, 199, 160, 180), width=3)
    draw.line((W - 170, H - 280, W - 410, H - 280), fill=(216, 199, 160, 180), width=3)


def cityline(page, y, alpha=180):
    im = city.resize((W, int(city.height * W / city.width)), Image.Resampling.LANCZOS)
    a = im.split()[3].point(lambda q: int(q * alpha / 255))
    im.putalpha(a)
    page.alpha_composite(im, (0, y))


def card(draw, box, radius=34, fill=LIGHT, outline=(216, 199, 160, 155), width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def logo(page, x, y, scale=1.0, full=True):
    d = ImageDraw.Draw(page)
    mark_w = int(300 * scale)
    mark = arch.resize((mark_w, int(arch.height * mark_w / arch.width)), Image.Resampling.LANCZOS)
    page.alpha_composite(mark, (int(x - mark.width / 2), int(y)))
    word_font = ImageFont.truetype(str(FONT_DIR / "FRANKB.TTF"), max(54, int(118 * scale)))
    sub_font = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), max(22, int(30 * scale)))
    rtl_text(d, x, y + mark.height + int(70 * scale), "גְּאוּלִי", word_font, NAVY)
    if full:
        rtl_text(d, x, y + mark.height + int(145 * scale), "קהילת ההורים של בית ספר גאולים בקעה", sub_font, OLIVE)


def header(page, title, eyebrow="גאולי"):
    d = ImageDraw.Draw(page)
    logo(page, W - 350, 70, 0.56)
    rtl_text(d, 935, 175, title, font_title, NAVY)
    rtl_text(d, 935, 290, eyebrow, font_body, GRAY)
    d.rounded_rectangle((330, 405, W - 330, 418), radius=7, fill=SAND)


def footer(page, n):
    d = ImageDraw.Draw(page)
    cityline(page, H - 230, 170)
    rtl_text(d, W // 2, H - 62, f"גאולי · מקום · אנשים · משמעות · {n}", font_tiny, NAVY)


def section_tag(draw, x, y, text):
    draw.rounded_rectangle((x - 155, y - 28, x + 155, y + 28), radius=28, fill=(255, 255, 255, 220))
    rtl_text(draw, x, y, text, font_tiny, OLIVE)


pages = []

# 1. Cover
p = page_base()
d = ImageDraw.Draw(p)
corner(d)
dot_grid(d, 190, 560, alpha=55)
dot_grid(d, W - 520, 470, alpha=55)
logo(p, W // 2, 760, 1.55)
dots(d, W // 2, 1660, 15)
rtl_text(d, W // 2, 1770, "מקום. אנשים. משמעות.", font_h, NAVY)
multiline(d, W // 2, 1905, "קהילה שמכירה את המקום, פוגשת את האנשים ופועלת יחד למען חינוך מיטיב לילדינו, תוך טיפוח שייכות, אחריות חברתית-ערכית וחיבור למקום שבו אנו חיים.", font_body, GRAY, 1580, 16)
rtl_text(d, W // 2, 2480, "שנת הלימודים תשפ״ז · 2026-2027", font_small, GRAY)
cityline(p, H - 260, 110)
pages.append(p)

# 2. Vision
p = page_base()
d = ImageDraw.Draw(p)
header(p, "קהילה. חינוך. משמעות.", "בונים יחד")
multiline(d, W // 2, 560, "קהילת הורי גאולים קמה מתוך מטרה וחזון משותף: להיות שותפים פעילים בעשייה הבית ספרית דרך שלושה צירים: מקום, אנשים ומשמעות. אנחנו מבקשות להכיר את המרחב שבו הילדים גדלים, לחזק קשרים בין הורים, תלמידים וצוות, ולהפוך את ההיכרות הזו ליוזמות חינוכיות, קהילתיות ומעשיות.", font_body, GRAY, 1780, 14)
axis = [
    ("המקום", "כל מרחב שהקהילה פוגשת: רחוב, גינה, חצר בית הספר, מסלול טיול או אתר בעיר."),
    ("האנשים", "בכל מקום יש אנשים, סיפורים וצרכים שונים. גאולי מחברת מתוך סקרנות, הקשבה וכבוד למגוון."),
    ("המשמעות", "ההיכרות מובילה לעשייה: יוזמה קטנה, שיפור במרחב, חיבור בין אנשים ותוכן שמספר סיפור.")
]
for i, (title, body) in enumerate(axis):
    x = 265 + i * 665
    y = 1085
    fill = [SAND, WHITE, NAVY][i]
    card(d, (x, y, x + 610, y + 560), 34, fill)
    dark = i == 2
    d.arc((x + 245, y + 70, x + 365, y + 190), 195, 345, fill=WHITE if dark else NAVY, width=5)
    rtl_text(d, x + 305, y + 255, title, font_h, WHITE if dark else NAVY)
    multiline(d, x + 520, y + 335, body, font_small, WHITE if dark else GRAY, 430, 8, False)
card(d, (330, 1840, W - 330, 2220), 36, (255, 255, 255, 235))
rtl_text(d, W // 2, 1930, "מה אנחנו רוצות לבנות", font_h, NAVY)
goals = ["קהילת הורים מעורבת, פעילה ומחויבת", "מרחב שמחזק נוכחות, קשרים ותחושת שייכות", "עשייה סביבתית וקהילתית סביב בית הספר והשכונה", "הנהגה שיתופית שנותנת דוגמה לילדים"]
for i, g in enumerate(goals):
    yy = 2030 + i * 55
    d.ellipse((W - 560, yy - 14, W - 532, yy + 14), fill=[SAND, OLIVE, NAVY, SAND][i])
    rtl_text(d, W - 590, yy, g, font_small_b, GRAY, "ra")
dots(d, W // 2, 2350)
rtl_text(d, W // 2, 2435, "מכירים את המקום · פוגשים את האנשים · יוצרים משמעות", font_body_b, NAVY)
footer(p, 2)
pages.append(p)

# 3. Principles
p = page_base()
d = ImageDraw.Draw(p)
header(p, "העקרונות שלנו", "שיתוף · קשב · שקיפות")
multiline(d, W // 2, 560, "שלושה עקרונות מנחים את קהילת ההורים של גאולי ומבדילים אותה מוועד רגיל: שותפות אמיתית, קשב שמאפשר לילדים לגדול, ושקיפות שמייצרת אמון.", font_body, GRAY, 1700, 14)
principles = [
    ("שיתוף", "שיתוף הדדי ובטוח בין הורים, מורים והנהלה. מודלינג לתלמידים לשיתוף פתוח ובריא."),
    ("מהפכת קשב", "דחיית הסמארטפון לאחר כיתה ו׳ ורצון כן לילדות מלאה, משחק, דמיון ושיחה אמיתית."),
    ("שקיפות", "כל החלטה, תקציב ומידע על מצב הכיתה ובית הספר ייעשו בכנות מלאה ובבהירות.")
]
for i, (title, body) in enumerate(principles):
    x = 260 + i * 670
    y = 905
    card(d, (x, y, x + 610, y + 650), 34, NAVY)
    rtl_text(d, x + 305, y + 130, title, font_h, WHITE)
    multiline(d, x + 520, y + 230, body, font_small, WHITE, 430, 10, False)
card(d, (385, 1730, W - 385, 2055), 36, (255, 255, 255, 238))
rtl_text(d, W // 2, 1820, "דרוש כפר שלם כדי לגדל ילד. גאולי תהיה הכפר הזה.", font_h, NAVY)
rtl_text(d, W // 2, 1930, "פתגם אפריקאי", font_small, GRAY)
values = [("אווירה מיטבית", "מרחב בטוח, מכבד ומעודד"), ("קהילה מחוברת", "חוויות, מסורות וקשרים משמעותיים"), ("חינוך ערכי", "ערכים בחיי היומיום"), ("סקרנות ולמידה", "יוזמה, יצירתיות ואהבת למידה")]
for i, (title, body) in enumerate(values):
    x = 300 + (i % 2) * 930
    y = 2240 + (i // 2) * 285
    card(d, (x, y, x + 820, y + 200), 28, [WHITE, SAND, WHITE, (138, 151, 70, 225)][i])
    rtl_text(d, x + 410, y + 70, title, font_body_b, NAVY if i != 3 else WHITE)
    rtl_text(d, x + 410, y + 135, body, font_small, GRAY if i != 3 else WHITE)
footer(p, 3)
pages.append(p)

# 4. Partnership
p = page_base()
d = ImageDraw.Draw(p)
header(p, "שותפות שמרגישים", "אמון ופעולה")
card(d, (315, 560, W - 315, 880), 38, NAVY)
multiline(d, W // 2, 650, "אנחנו מביאות אמון, פעולה, פתיחות ושותפות אמיתית. נבקש לפעול יחד מתוך כבוד, הבנה וקשרים פתוחים, כך שכל משפחה תרגיש שיש לה מקום וקול.", font_body, WHITE, 1680, 16)
parts = [
    ("אמון", "בבחירות שלנו, בצוות ובהצלחת הדרך המשותפת."),
    ("פעולה", "עשייה קטנה ומעשית שמתחברת לצורך אמיתי."),
    ("פתיחות", "רצון לשמוע, להבין ולהיות נגישים לתהליכים."),
    ("שותפות אמיתית", "זמן, מחשבה והתמסרות למען הילדים.")
]
for i, (title, body) in enumerate(parts):
    x = 285 + (i % 2) * 960
    y = 1060 + (i // 2) * 455
    fill = [WHITE, SAND, (138, 151, 70, 225), NAVY][i]
    card(d, (x, y, x + 850, y + 320), 34, fill)
    dark = i in (2, 3)
    d.ellipse((x + 690, y + 60, x + 755, y + 125), fill=WHITE if dark else [SAND, OLIVE, NAVY, SAND][i])
    rtl_text(d, x + 425, y + 100, title, font_h, WHITE if dark else NAVY)
    multiline(d, x + 760, y + 175, body, font_small, WHITE if dark else GRAY, 650, 8, False)
card(d, (330, 2100, W - 330, 2580), 42, (255, 255, 255, 238))
rtl_text(d, W // 2, 2200, "איך השותפות נראית בפועל?", font_h, NAVY)
bullets = ["מבט קדימה: חושבים יחד, מתכננים ומשפרים כל הזמן", "התנדבויות מעשירות: כוח ההורים כמנוע שמוביל ומסייע", "חיזוק קשרים: מפגשים ופעילויות שמחברים בין הורים לילדים", "תקשורת פתוחה: שיח מכבד, ישיר, מעודכן ושקוף"]
for i, b in enumerate(bullets):
    yy = 2310 + i * 62
    d.ellipse((W - 610, yy - 14, W - 582, yy + 14), fill=[SAND, OLIVE, NAVY, SAND][i])
    rtl_text(d, W - 640, yy, b, font_small_b, GRAY, "ra")
footer(p, 4)
pages.append(p)

# 5. Circles
p = page_base()
d = ImageDraw.Draw(p)
header(p, "קהילת ההורים והתלמידים", "מעגלי עשייה פתוחים")
multiline(d, W // 2, 550, "במקום ועד מרכזי אחד, קהילת גאולי פועלת במבנה פתוח, מבוזר ומעשי. כל הורה יכול להצטרף למעגל שמתאים לו, ליזום, לקחת אחריות ולהוביל פעולה קטנה או גדולה.", font_body, GRAY, 1740, 14)
circles = [
    ("מעגל מקום", "סיורים במרחב הציבורי של השכונה והעיר, שימור פארק המסילה, ימי ניקיון, גינות קהילתיות והיכרות עם סיפורים בירושלים."),
    ("מעגל אנשים", "קבלת משפחות חדשות, מפגשי היכרות, ירידים ואירועים קהילתיים, וסיוע הדדי בין משפחות."),
    ("מעגל משמעות", "התנדבות משפחתית, סדנאות הורים וילדים, יוזמות חברתיות, סיפורי משפחה ומורשת המקום.")
]
for i, (title, body) in enumerate(circles):
    x = 245 + i * 675
    y = 900
    fill = [SAND, WHITE, NAVY][i]
    card(d, (x, y, x + 610, y + 720), 36, fill)
    dark = i == 2
    rtl_text(d, x + 305, y + 115, title, font_h, WHITE if dark else NAVY)
    multiline(d, x + 520, y + 210, body, font_small, WHITE if dark else GRAY, 430, 9, False)
card(d, (260, 1785, W - 260, 2275), 42, (255, 255, 255, 238))
rtl_text(d, W // 2, 1878, "מעגלי תלמידים", font_h, NAVY)
multiline(d, W // 2, 1975, "גם הילדים פועלים במעגלים קבועים כדי ללמוד אחריות, שייכות ועשייה דרך אותה שפה: מקום, ילדים ומשמעות.", font_body, GRAY, 1600, 14)
students = [("מעגל מקום", "כיתה, חצר, פינת טבע ומרחבים משותפים"), ("מעגל ילדים", "לשים לב מי חדש, מי לבד ומי צריך הזמנה"), ("מעגל משמעות", "סיפורי משפחה, פינת ספרים, תערוכות ונתינה")]
for i, (title, body) in enumerate(students):
    x = 380 + i * 575
    y = 2420
    d.rounded_rectangle((x, y, x + 470, y + 210), radius=26, fill=[WHITE, SAND, NAVY][i], outline=(216, 199, 160, 160), width=2)
    rtl_text(d, x + 235, y + 70, title, font_body_b, WHITE if i == 2 else NAVY)
    multiline(d, x + 405, y + 125, body, font_tiny, WHITE if i == 2 else GRAY, 350, 4, False)
footer(p, 5)
pages.append(p)

# 6. Opening plan
p = page_base()
d = ImageDraw.Draw(p)
header(p, "תוכנית הפתיחה", "עוגנים וסדירויות")
rtl_text(d, W // 2, 560, "ארבע פעולות הכנה עוד לפני היום הראשון ללימודים", font_body_b, NAVY)
opening = [("סקר הורים", "מי אני, מה אני יכולה לתרום, ואיזה צוות מתאים לי."), ("לוח ימי הולדת", "לוח שנתי כיתתי שמייצר תשומת לב וקשר."), ("מיפוי צוות מקצועי", "מי מלמד, מתי, ומה הקשר ההורי הנכון."), ("הכנת הכיתה", "צביעה, קישוט וסידור מרחב שמרגיש כמו בית.")]
for i, (title, body) in enumerate(opening):
    x = 300 + (i % 2) * 930
    y = 760 + (i // 2) * 410
    card(d, (x, y, x + 820, y + 295), 34, [WHITE, SAND, WHITE, NAVY][i])
    d.ellipse((x + 680, y + 55, x + 750, y + 125), fill=[NAVY, OLIVE, SAND, WHITE][i])
    rtl_text(d, x + 410, y + 98, title, font_h, WHITE if i == 3 else NAVY)
    multiline(d, x + 735, y + 170, body, font_small, WHITE if i == 3 else GRAY, 620, 8, False)
card(d, (260, 1740, W - 260, 2880), 44, (255, 255, 255, 238))
rtl_text(d, W // 2, 1835, "שנת הלימודים שלנו", font_title, NAVY)
months = [
    ("אוגוסט", "פיקניק היכרות, סקר הורים, הכנת הכיתה ומתנות פתיחה לצוות."),
    ("ספטמבר", "טקס פתיחת שנה, אימוץ כיתה א׳, ברכות לשנה טובה וטיול משפחות."),
    ("דצמבר", "טיול עששיות בחנוכה ופעילות הורים וילדים לסיכום מחצית."),
    ("ינואר-פברואר", "סיור שכונתי משפחתי והיכרות עם בקעה ופינות נסתרות."),
    ("מרץ-אפריל", "פורים, משלוחי מנות, סדר כיתתי ואירוע פסח משותף."),
    ("מאי-יוני", "פיקניק סוף שנה, אלבום דיגיטלי, חגיגת הישגים וטקס מעבר.")
]
for i, (m, b) in enumerate(months):
    x = 350 + (i % 2) * 860
    y = 1990 + (i // 2) * 255
    d.rounded_rectangle((x, y, x + 730, y + 168), radius=24, fill=(248, 246, 241, 245), outline=(216, 199, 160, 135), width=2)
    rtl_text(d, x + 365, y + 48, m, font_body_b, NAVY)
    multiline(d, x + 650, y + 90, b, font_tiny, GRAY, 560, 4, False)
footer(p, 6)
pages.append(p)

# 7. Anchor rhythms
p = page_base()
d = ImageDraw.Draw(p)
header(p, "שגרות שמחזיקות קהילה", "מה חוזר לאורך השנה")
card(d, (300, 570, W - 300, 980), 42, NAVY)
multiline(d, W // 2, 680, "כדי שהקהילה לא תהיה אירוע חד פעמי, נבנים עוגנים קבועים: מפגשים, יוזמות קטנות, תקשורת ברורה ותיעוד תוצרים.", font_body, WHITE, 1660, 16)
rhythms = [
    ("מפגש", "מפגש קהילתי קצר אחת לתקופה, סביב צורך או רעיון."),
    ("פעולה", "פעולה קטנה ומעשית שמחברת ילדים, הורים וצוות."),
    ("שיתוף", "עדכון בהיר לקהילה: מה עשינו, מי הצטרף ומה הצעד הבא."),
    ("למידה", "איסוף משוב קצר ושיפור מתמיד של הדרך.")
]
for i, (title, body) in enumerate(rhythms):
    x = 270 + (i % 2) * 960
    y = 1200 + (i // 2) * 520
    fill = [WHITE, SAND, (138, 151, 70, 225), WHITE][i]
    card(d, (x, y, x + 850, y + 380), 36, fill)
    dark = i == 2
    d.ellipse((x + 685, y + 65, x + 765, y + 145), fill=[SAND, NAVY, NAVY, OLIVE][i])
    rtl_text(d, x + 425, y + 120, title, font_h, WHITE if dark else NAVY)
    multiline(d, x + 760, y + 205, body, font_small, WHITE if dark else GRAY, 650, 8, False)
dots(d, W // 2, 2440, 16)
rtl_text(d, W // 2, 2545, "קהילה נוצרת מחזרתיות טובה: עוד מפגש, עוד חיבור, עוד פעולה קטנה.", font_h, NAVY)
footer(p, 7)
pages.append(p)

# 8. Closing / commitment
p = page_base()
d = ImageDraw.Draw(p)
corner(d)
dot_grid(d, 200, 520, alpha=50)
dot_grid(d, W - 520, 520, alpha=50)
logo(p, W // 2, 500, 1.05)
rtl_text(d, W // 2, 1280, "אמנת הקשב", font_title, NAVY)
multiline(d, W // 2, 1410, "בחירה משותפת לתת לילדים ילדות של נוכחות, משחק חופשי, שיחה אמיתית ודמיון. כאשר כולנו מתחייבים יחד, כל ילד מרגיש שיש לו גב.", font_body, GRAY, 1620, 16)
card(d, (420, 1780, W - 420, 2290), 42, NAVY)
rtl_text(d, W // 2, 1885, "המחויבות שלנו", font_h, WHITE)
commit = ["נעדיף טלפון בסיסי לצורכי תקשורת", "נתמוך זה בזה מול לחץ חברתי", "נגביל זמני מסך בבית ונשתף בדילמות", "נהיה דוגמה אישית לשימוש מושכל במסכים"]
for i, line in enumerate(commit):
    yy = 1995 + i * 72
    d.ellipse((W - 680, yy - 15, W - 650, yy + 15), fill=[SAND, OLIVE, SAND, OLIVE][i])
    rtl_text(d, W - 710, yy, line, font_small_b, WHITE, "ra")
multiline(d, W // 2, 2490, "גאולי היא מקום אחד לאנשים רבים עם משמעות משותפת. כאן כל משפחה שייכת, כל קול נשמע, וכל תרומה - גדולה או קטנה - בונה קהילה שהילדים שלנו יגדלו בתוכה.", font_body_b, NAVY, 1700, 16)
d.text((W // 2, 2855), "www.geuli.co.il", font=font_body_b, fill=NAVY, anchor="mm")
rtl_text(d, W // 2, 2940, "קהילת ההורים של בית ספר גאולים בקעה, ירושלים", font_small, GRAY)
cityline(p, H - 260, 150)
pages.append(p)

rgb = []
for path, page in zip(PREVIEWS, pages):
    out = page.convert("RGB")
    out.save(path, quality=95)
    rgb.append(out)
rgb[0].save(PDF, save_all=True, append_images=rgb[1:], resolution=300.0)
print(PDF.resolve())
for path in PREVIEWS:
    print(path.resolve())
