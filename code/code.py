"""
Two-column exact-replica generator for page 1 (ReportLab)

- A4 page, margins = 1.27 cm
- Two columns: width = 9.18 cm each, spacing = 0.1 cm (fits usable width)
- Header image (1600x400 ratio) at top inside margins
- Page background color: Blue Accent 5 Lighter 60% (approx)
- Q&A: Nirmala UI, size 8, leading = 8 (1.0)
- Numbers: 0.1 cm from left edge of the column; text starts at 0.7 cm from left edge of the column
- Footer: three-part (left/center/right) at baseline = 1.27 cm, Badoni MT size 11
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# -----------------------
# Files & font names
# -----------------------
HEADER_IMAGE = "header.png"
NIRMALA_TTF = "Nirmala.ttf"
BADONI_TTF = "BadoniMT.ttf"

NIRMALA_FACE = "NirmalaUI_Custom"
BADONI_FACE  = "BadoniMT_Custom"

# -----------------------
# Page / layout constants
# -----------------------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm                       # all four margins exactly 1.27 cm
FOOTER_BASELINE = 1.27 * cm              # footer baseline exactly 1.27 cm from bottom
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Two-column settings (as provided)
COL_WIDTH_CM = 9.18                       # cm
COL_SPACING_CM = 0.1                      # cm
COL_WIDTH = COL_WIDTH_CM * cm
COL_SPACING = COL_SPACING_CM * cm

# Sanity: total should match usable width (9.18*2 + 0.1 = 18.46 cm)
assert abs((COL_WIDTH * 2 + COL_SPACING) - USABLE_WIDTH) < 1e-6, "Column widths+spacing do not match usable width"

# Header keeps 4:1 ratio (1600x400)
HEADER_RATIO = 400.0 / 1600.0
HEADER_HEIGHT = (USABLE_WIDTH) * HEADER_RATIO
GAP_AFTER_HEADER = 0.25 * cm

# Q/A layout specifics
NUMBER_OFFSET_INSIDE_COL = 0.1 * cm    # number from left edge of column
TEXT_START_INSIDE_COL = 0.7 * cm       # text start from left edge of column
QA_FONT_SIZE = 8
QA_LEADING = 8.0                        # line spacing 1.0 -> leading = font size = 8
LINE_GAP_BETWEEN_ITEMS = 0.1 * cm

# Footer font size
FOOTER_FONT_SIZE = 11

# Page background RGB approximation for "Blue, Accent 5, Lighter 60%"
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)

# -----------------------
# Register fonts if available
# -----------------------
def try_register(ttf_path, face_name):
    if os.path.isfile(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont(face_name, ttf_path))
            print(f"Registered font '{face_name}' from {ttf_path}")
            return True
        except Exception as e:
            print("Font register error:", e)
    else:
        print(f"Font file {ttf_path} not found in working folder.")
    return False

nirmala_ok = try_register(NIRMALA_TTF, NIRMALA_FACE)
badoni_ok  = try_register(BADONI_TTF, BADONI_FACE)

if not nirmala_ok:
    print("Nirmala UI not found — falling back to Helvetica for QA text.")
    NIRMALA_FACE = "Helvetica"
if not badoni_ok:
    print("Badoni MT not found — falling back to Times-Roman for footer.")
    BADONI_FACE = "Times-Roman"

# -----------------------
# Content (page 1)
# -----------------------
# Footer (three-part) — user confirmed these belong to footer
footer_left   = "Page 1 of 13"
footer_center = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
footer_right  = "https://dbggurukulam.com"

section_heading = "Quick revision: One-liner questions and answers"

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

# -----------------------
# Helper: measure string width
# -----------------------
def string_width(text, font_name, font_size):
    try:
        return pdfmetrics.stringWidth(text, font_name, font_size)
    except:
        return pdfmetrics.stringWidth(text, "Helvetica", font_size)

# -----------------------
# Create PDF
# -----------------------
OUTFILE = "page1_two_columns_exact.pdf"
c = canvas.Canvas(OUTFILE, pagesize=A4)

# 1) page background
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# 2) header image inside margins
header_x = MARGIN
header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
if os.path.isfile(HEADER_IMAGE):
    c.drawImage(HEADER_IMAGE, header_x, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
else:
    c.setStrokeColorRGB(0.6,0.6,0.6)
    c.rect(header_x, header_y, USABLE_WIDTH, HEADER_HEIGHT, stroke=1, fill=0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x + USABLE_WIDTH/2, header_y + HEADER_HEIGHT/2, "HEADER IMAGE MISSING - put header.png here")

# 3) Section heading under header (single-line across page)
heading_y = header_y - GAP_AFTER_HEADER - (0.05 * cm)
c.setFont("Times-Bold", 11)
c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, heading_y, section_heading)

# 4) Two-column Q&A block
start_y = heading_y - (0.5 * cm)
current_y_col = [start_y, start_y]   # y for col0 and col1
col_x_start = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
col_right_limit = [col_x_start[0] + COL_WIDTH, col_x_start[1] + COL_WIDTH]
col_avail_width = [COL_WIDTH - TEXT_START_INSIDE_COL, COL_WIDTH - TEXT_START_INSIDE_COL]  # available for text portion (text_x relative to col_x_start)
bottom_limit = FOOTER_BASELINE + (0.35 * cm)

# Prepare iteration across QAs, fill first column top->down, then second
col = 0
qa_index = 0
while qa_index < len(qa_lines):
    qa = qa_lines[qa_index]
    # parse number and rest
    if '.' in qa:
        num_part, rest = qa.split('.', 1)
        num_text = num_part.strip() + '.'
        rest = rest.strip()
    else:
        num_text = ""
        rest = qa

    # wrap rest into lines that fit the column text area
    words = rest.split()
    lines = []
    cur = ""
    avail_width_for_text = col_avail_width[col]
    for w in words:
        candidate = (cur + " " + w).strip() if cur else w
        if string_width(candidate, NIRMALA_FACE, QA_FONT_SIZE) <= avail_width_for_text:
            cur = candidate
        else:
            if cur == "":
                lines.append(candidate)
                cur = ""
            else:
                lines.append(cur)
                cur = w
    if cur:
        lines.append(cur)

    needed_height = len(lines) * QA_LEADING
    # check if fits in current column
    if current_y_col[col] - needed_height < bottom_limit:
        # if we're in first column, move to second column
        if col == 0:
            col = 1
            # continue without incrementing qa_index (attempt again in new column)
            continue
        else:
            # second column full — stop rendering (page 1 full)
            break

    # draw number and wrapped lines in current column
    number_x = col_x_start[col] + NUMBER_OFFSET_INSIDE_COL
    text_x = col_x_start[col] + TEXT_START_INSIDE_COL
    y = current_y_col[col]
    # draw number at first baseline
    try:
        c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
    except:
        c.setFont("Helvetica", QA_FONT_SIZE)
    if num_text:
        c.drawString(number_x, y, num_text)
    for ln in lines:
        try:
            c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
        except:
            c.setFont("Helvetica", QA_FONT_SIZE)
        c.drawString(text_x, y, ln)
        y -= QA_LEADING

    # update current_y for this column (add small gap)
    current_y_col[col] = y - LINE_GAP_BETWEEN_ITEMS

    # next QA
    qa_index += 1

# 5) Footer (left, center, right) exactly at baseline = 1.27 cm from bottom
try:
    c.setFont(BADONI_FACE, FOOTER_FONT_SIZE)
except:
    c.setFont("Times-Roman", FOOTER_FONT_SIZE)
c.setFillColorRGB(0,0,0)
# left
c.drawString(MARGIN, FOOTER_BASELINE, footer_left)
# center
c.drawCentredString(PAGE_WIDTH/2.0, FOOTER_BASELINE, footer_center)
# right
c.drawRightString(PAGE_WIDTH - MARGIN, FOOTER_BASELINE, footer_right)

c.showPage()
c.save()

print("Saved PDF:", OUTFILE)
if not nirmala_ok:
    print("NOTE: Nirmala UI not found; used fallback font. To match exactly, place 'Nirmala.ttf' in script folder.")
if not badoni_ok:
    print("NOTE: Badoni MT not found; used fallback font. To match exactly, place 'BadoniMT.ttf' in script folder.")
