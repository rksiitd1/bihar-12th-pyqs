"""
Updated two-column page1 generator with:
- Section heading in ALGERIAN, 12pt, ALL CAPS, left-aligned
- Horizontal rule below heading: full usable width (inside margins), 1 pt thick, gray stroke
- Two columns (9.18 cm each, 0.1 cm spacing), Nirmala UI QA, footer area height 1.25 cm with footer text at top of footer.
- Place header.png, Algerian.ttf, Nirmala.ttf, BadoniMT.ttf in the same folder to get exact fonts/images.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ---------- files & fonts ----------
HEADER_IMAGE = "header.png"
ALGERIAN_TTF = "Algerian.ttf"
NIRMALA_TTF = "Nirmala.ttf"
BADONI_TTF = "BadoniMT.ttf"

ALG_FACE = "Algerian_Custom"
NIRMALA_FACE = "NirmalaUI_Custom"
BADONI_FACE = "BadoniMT_Custom"

# ---------- page/layout ----------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm                    # page margins
FOOTER_SECTION_HEIGHT = 1.25 * cm     # footer area height measured from bottom
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# two-column specs
COL_WIDTH_CM = 9.18
COL_SPACING_CM = 0.1
COL_WIDTH = COL_WIDTH_CM * cm
COL_SPACING = COL_SPACING_CM * cm
assert abs((COL_WIDTH * 2 + COL_SPACING) - USABLE_WIDTH) < 1e-4, "Columns don't sum to usable width"

# header ratio (1600x400 => 4:1)
HEADER_RATIO = 400.0 / 1600.0
HEADER_HEIGHT = USABLE_WIDTH * HEADER_RATIO
GAP_AFTER_HEADER = 0.25 * cm

# QA text settings
QA_FONT_SIZE = 8
QA_LEADING = 8.0
NUMBER_OFFSET_INSIDE_COL = 0.1 * cm
TEXT_START_INSIDE_COL = 0.7 * cm
LINE_GAP_BETWEEN_ITEMS = 0.1 * cm

# heading settings
HEADING_FONT_SIZE = 12
HEADING_FONT_FACE = ALG_FACE
HEADING_COLOR = (0, 0, 0)  # black

# horizontal rule
HR_COLOR = (0.5, 0.5, 0.5)   # gray
HR_THICKNESS_PT = 1.0       # 1 pt

# footer font size
FOOTER_FONT_SIZE = 11

# page background (Blue Accent 5 Lighter 60% approx)
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)

# ---------- try to register fonts ----------
def try_register(ttf_path, face_name):
    if os.path.isfile(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont(face_name, ttf_path))
            print(f"Registered font '{face_name}' from {ttf_path}")
            return True
        except Exception as e:
            print("Font register error for", ttf_path, ":", e)
    else:
        print(f"Font file {ttf_path} not found in working folder.")
    return False

alg_ok = try_register(ALGERIAN_TTF, ALG_FACE)
nirmala_ok = try_register(NIRMALA_TTF, NIRMALA_FACE)
badoni_ok  = try_register(BADONI_TTF, BADONI_FACE)

# fallbacks
if not alg_ok:
    ALG_FACE = "Times-Bold"
if not nirmala_ok:
    NIRMALA_FACE = "Helvetica"
if not badoni_ok:
    BADONI_FACE = "Times-Roman"

# ---------- content ----------
footer_left   = "Page 1 of 13"
footer_center = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
footer_right  = "https://dbggurukulam.com"
section_heading = "Quick revision: One-liner questions and answers"

# Q/A lines (1-60)
qa_lines = [
"1. What is the reproductive part of a flowering plant? - The flower.",
"2. What is the male part of a flower called? - The Androecium.",
"3. The androecium is made of what units? - Stamens.",
"4. A stamen has which two parts? - The anther and the filament.",
"5. What part of the anther makes pollen? - The microsporangium (or pollen sac).",
"6. What is the ploidy of a microspore mother cell? - Diploid (2n).",
"7. How do microspore mother cells form microspores? - Through meiosis.",
"8. What is the ploidy of a pollen grain? - Haploid (n).",
"9. What is the hard outer layer of pollen? - The exine.",
"10. What tough material makes the exine? - Sporopollenin.",
"11. What is the thin inner layer of pollen? - The intine.",
"12. Name the two cells in a mature pollen grain. - The vegetative cell and generative cell.",
"13. Which pollen cell is larger and forms the pollen tube? - The vegetative cell.",
"14. Which pollen cell forms the two male gametes? - The generative cell.",
"15. What is the female part of a flower called? - The Gynoecium (or pistil).",
"16. A pistil has which three parts? - Stigma, style, and ovary.",
"17. Which part of the pistil catches pollen? - The stigma.",
"18. What structure is found inside the ovary? - The ovule.",
"19. After fertilization, what does the ovule become? - The seed.",
"20. What sac inside the ovule holds the egg cell? - The embryo sac.",
"21. What is the ploidy of a megaspore mother cell? - Diploid (2n).",
"22. Meiosis of a megaspore mother cell produces how many megaspores? - Four.",
"23. How many of the four megaspores usually survive? - Only one.",
"24. A typical embryo sac has how many cells and nuclei? - 7 cells, 8 nuclei.",
"25. Name the three cells at the micropylar end. - One egg cell and two synergids.",
"26. What do we call the egg cell and its two synergids? - The egg apparatus.",
"27. Name the three cells at the opposite (chalazal) end. - The antipodal cells.",
"28. What is the large cell in the middle of the embryo sac? - The central cell.",
"29. What two nuclei are in the central cell? - The two polar nuclei.",
"30. What is the transfer of pollen to a stigma called? - Pollination.",
"31. Pollination within the same flower is called what? - Autogamy.",
"32. Pollination between flowers on the same plant is called what? - Geitonogamy.",
"33. Pollination between flowers on different plants is called what? - Xenogamy.",
"34. What is pollination by wind called? - Anemophily.",
"35. What is pollination by insects called? - Entomophily.",
"36. What is pollination by water called? - Hydrophily.",
"37. Can the male gametes in flowering plants swim? - No, they are non-motile.",
"38. What tube grows from the pollen grain to the ovule? - The pollen tube.",
"39. How many male gametes does the pollen tube deliver? - Two.",
"40. What is the fusion of a male gamete and the egg cell? - Syngamy (fertilization).",
"41. Syngamy results in what new cell? - The zygote.",
"42. What is a zygote's ploidy? - Diploid (2n).",
"43. What is the second fertilization event in angiosperms? - Triple fusion.",
"44. What three nuclei fuse during triple fusion? - One male gamete and two polar nuclei.",
"45. Triple fusion forms what special nucleus? - The Primary Endosperm Nucleus (PEN).",
"46. What is the endosperm's ploidy? - Triploid (3n).",
"47. What do we call syngamy and triple fusion happening together? - Double fertilization.",
"48. What is the main job of the endosperm? - To feed the growing embryo.",
"49. The zygote grows into what structure? - The embryo.",
"50. What part of the ovule becomes the seed coat? - The integuments.",
"51. After fertilization, what does the ovary become? - The fruit.",
"52. What do we call a fruit that forms without fertilization? - A parthenocarpic fruit.",
"53. The banana is a natural example of what? - Parthenocarpy.",
"54. A fruit that develops only from the ovary is a what? - A true fruit.",
"55. A fruit that develops from more than the ovary is a what? - A false fruit.",
"56. The apple is a common example of what kind of fruit? - A false fruit.",
"57. An embryo developing from an unfertilized egg is called what? - Parthenogenesis.",
"58. What is it called when seeds form without any fertilization? - Apomixis.",
"59. What do we call it when a single seed has multiple embryos? - Polyembryony.",
"60. Polyembryony is common in which type of fruit? - Citrus fruits."
]

# ---------- helper ----------
def string_width(text, font_name, font_size):
    try:
        return pdfmetrics.stringWidth(text, font_name, font_size)
    except:
        return pdfmetrics.stringWidth(text, "Helvetica", font_size)

# ---------- create pdf ----------
OUTFILE = "page1_two_columns_heading_algerian_hr.pdf"
c = canvas.Canvas(OUTFILE, pagesize=A4)

# background
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# header image
header_x = MARGIN
header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
if os.path.isfile(HEADER_IMAGE):
    c.drawImage(HEADER_IMAGE, header_x, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
else:
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.rect(header_x, header_y, USABLE_WIDTH, HEADER_HEIGHT, stroke=1, fill=0)
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x + USABLE_WIDTH/2, header_y + HEADER_HEIGHT/2, "HEADER IMAGE MISSING")

# heading: Algerian, 12pt, ALL CAPS, left-aligned at margin
heading_y = header_y - GAP_AFTER_HEADER - (0.05 * cm)
heading_text = section_heading.upper()
try:
    c.setFont(HEADING_FONT_FACE, HEADING_FONT_SIZE)
except:
    c.setFont("Times-Bold", HEADING_FONT_SIZE)
c.setFillColorRGB(*HEADING_COLOR)
c.drawString(MARGIN, heading_y, heading_text)

# horizontal rule immediately below heading (full usable width inside margins), gray, 1 pt thick
hr_y = heading_y - (0.18 * cm)  # small gap below text before hr; tweak if needed
c.setStrokeColorRGB(*HR_COLOR)
c.setLineWidth(HR_THICKNESS_PT)
c.line(MARGIN, hr_y, PAGE_WIDTH - MARGIN, hr_y)

# start two-column block below the rule
start_y = hr_y - (0.4 * cm)
current_y = [start_y, start_y]
col_x_start = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
bottom_limit = FOOTER_SECTION_HEIGHT + (0.35 * cm)    # don't intrude into footer area

col = 0
i = 0
while i < len(qa_lines):
    qa = qa_lines[i]
    if '.' in qa:
        num_part, rest = qa.split('.', 1)
        num_text = num_part.strip() + '.'
        rest = rest.strip()
    else:
        num_text = ""
        rest = qa

    # wrap text for column
    avail_width = COL_WIDTH - TEXT_START_INSIDE_COL
    words = rest.split()
    lines = []
    cur = ""
    for w in words:
        cand = (cur + " " + w).strip() if cur else w
        if string_width(cand, NIRMALA_FACE, QA_FONT_SIZE) <= avail_width:
            cur = cand
        else:
            if cur == "":
                lines.append(cand)
                cur = ""
            else:
                lines.append(cur)
                cur = w
    if cur:
        lines.append(cur)

    needed_h = len(lines) * QA_LEADING
    if current_y[col] - needed_h < bottom_limit:
        if col == 0:
            col = 1
            continue
        else:
            break

    # draw number & lines in the current column
    num_x = col_x_start[col] + NUMBER_OFFSET_INSIDE_COL
    text_x = col_x_start[col] + TEXT_START_INSIDE_COL
    y = current_y[col]
    try:
        c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
    except:
        c.setFont("Helvetica", QA_FONT_SIZE)
    if num_text:
        c.drawString(num_x, y, num_text)
    for ln in lines:
        c.drawString(text_x, y, ln)
        y -= QA_LEADING

    current_y[col] = y - LINE_GAP_BETWEEN_ITEMS
    i += 1

# footer: footer area height is FOOTER_SECTION_HEIGHT from bottom; place text near the top edge of that area
footer_top_y = FOOTER_SECTION_HEIGHT
footer_text_y = footer_top_y - (0.12 * cm)

try:
    c.setFont(BADONI_FACE, FOOTER_FONT_SIZE)
except:
    c.setFont("Times-Roman", FOOTER_FONT_SIZE)
c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, footer_text_y, footer_left)
c.drawCentredString(PAGE_WIDTH/2.0, footer_text_y, footer_center)
c.drawRightString(PAGE_WIDTH - MARGIN, footer_text_y, footer_right)

c.showPage()
c.save()

print("Saved PDF:", OUTFILE)
if not alg_ok:
    print("ALGERIAN font not found; used Times-Bold instead; to match exactly place 'Algerian.ttf' in the script folder.")
if not nirmala_ok:
    print("Nirmala UI not found; used fallback font (Helvetica); place 'Nirmala.ttf' for exact match.")
if not badoni_ok:
    print("Badoni MT not found; used fallback (Times-Roman); place 'BadoniMT.ttf' for exact match.")
