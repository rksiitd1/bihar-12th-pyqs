# updated two-column page1 generator with footer SECTION height = 1.25 cm
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
MARGIN = 1.27 * cm                       # page margins
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Two-column settings
COL_WIDTH_CM = 9.18
COL_SPACING_CM = 0.1
COL_WIDTH = COL_WIDTH_CM * cm
COL_SPACING = COL_SPACING_CM * cm
assert abs((COL_WIDTH * 2 + COL_SPACING) - USABLE_WIDTH) < 1e-6, "Column widths+spacing must equal usable width"

# Header (4:1)
HEADER_RATIO = 400.0 / 1600.0
HEADER_HEIGHT = USABLE_WIDTH * HEADER_RATIO
GAP_AFTER_HEADER = 0.25 * cm

# Q/A
NUMBER_OFFSET_INSIDE_COL = 0.1 * cm
TEXT_START_INSIDE_COL = 0.7 * cm
QA_FONT_SIZE = 8
QA_LEADING = 8.0
LINE_GAP_BETWEEN_ITEMS = 0.1 * cm

# Footer SECTION (height measured from bottom) and text padding from top of footer
FOOTER_SECTION_HEIGHT = 1.25 * cm       # footer area height from bottom
FOOTER_TEXT_TOP_PADDING = 0.12 * cm     # small gap from top of footer area to footer text baseline
FOOTER_FONT_SIZE = 11

# Page background (approx Blue Accent 5 Lighter 60%)
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)

# -----------------------
# Register fonts if available
# -----------------------
def try_register(ttf_path, face_name):
    if os.path.isfile(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont(face_name, ttf_path))
            return True
        except Exception:
            return False
    return False

nirmala_ok = try_register(NIRMALA_TTF, NIRMALA_FACE)
badoni_ok  = try_register(BADONI_TTF, BADONI_FACE)
if not nirmala_ok: NIRMALA_FACE = "Helvetica"
if not badoni_ok:  BADONI_FACE  = "Times-Roman"

# -----------------------
# Content
# -----------------------
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
# Helpers
# -----------------------
def string_width(text, font_name, font_size):
    try:
        return pdfmetrics.stringWidth(text, font_name, font_size)
    except:
        return pdfmetrics.stringWidth(text, "Helvetica", font_size)

# -----------------------
# Render PDF
# -----------------------
OUTFILE = "page1_two_columns_footer_section_1.25cm.pdf"
c = canvas.Canvas(OUTFILE, pagesize=A4)

# page background
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# header image
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

# section heading
heading_y = header_y - GAP_AFTER_HEADER - (0.05 * cm)
c.setFont("Times-Bold", 11)
c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, heading_y, section_heading)

# two columns: positions
start_y = heading_y - (0.5 * cm)
current_y_col = [start_y, start_y]
col_x_start = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
bottom_limit = FOOTER_SECTION_HEIGHT + (0.18 * cm)  # safety above footer; keep a small gap above the footer's top

# layout QA into columns (flow first col then second)
col = 0
qa_index = 0
while qa_index < len(qa_lines):
    qa = qa_lines[qa_index]
    # parse
    if '.' in qa:
        num_part, rest = qa.split('.', 1)
        num_text = num_part.strip() + '.'
        rest = rest.strip()
    else:
        num_text = ""
        rest = qa
    # wrap rest for column text area
    avail_text_width = COL_WIDTH - TEXT_START_INSIDE_COL
    words = rest.split()
    lines = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip() if cur else w
        if string_width(candidate, NIRMALA_FACE, QA_FONT_SIZE) <= avail_text_width:
            cur = candidate
        else:
            if cur == "":
                lines.append(candidate); cur = ""
            else:
                lines.append(cur); cur = w
    if cur: lines.append(cur)
    needed_h = len(lines) * QA_LEADING
    # fit check
    if current_y_col[col] - needed_h < bottom_limit:
        if col == 0:
            col = 1
            continue
        else:
            break
    # draw in column
    number_x = col_x_start[col] + NUMBER_OFFSET_INSIDE_COL
    text_x = col_x_start[col] + TEXT_START_INSIDE_COL
    y = current_y_col[col]
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
    current_y_col[col] = y - LINE_GAP_BETWEEN_ITEMS
    qa_index += 1

# Footer: footER SECTION is FOOTER_SECTION_HEIGHT tall; place footer text near the TOP of that section
footer_text_y = FOOTER_SECTION_HEIGHT - FOOTER_TEXT_TOP_PADDING  # y measured from bottom
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
print("Saved:", OUTFILE)
if not nirmala_ok:
    print("NOTE: Nirmala UI not found; used fallback 'Helvetica' — place 'Nirmala.ttf' for exact match.")
if not badoni_ok:
    print("NOTE: Badoni MT not found; used fallback 'Times-Roman' — place 'BadoniMT.ttf' for exact match.")
