"""
Final two-column page1 generator with smart wrapping logic.

- If a question exceeds 80% of the column width, it wraps, and the answer
  is always placed on the lines below it.
- Otherwise, it attempts a single-line layout if space permits.
- All spacing rules from the original spec are maintained.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
import os

# ---------- files & fonts ----------
HEADER_IMAGE = "header.png"
ALGERIAN_TTF = "Algerian.ttf"
NIRMALA_TTF = "Nirmala.ttf"
BADONI_TTF = "BadoniMT.ttf"

ALG_FACE = "Algerian_Custom"
NIRMALA_FACE = "NirmalaUI_Custom"
BADONI_FACE = "BadoniMT_Custom"
NIRMALA_BI_FACE = "Helvetica-BoldOblique"

# ---------- page/layout ----------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm
FOOTER_SECTION_HEIGHT = 1.25 * cm
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

COL_WIDTH = 9.18 * cm
COL_SPACING = 0.1 * cm
assert abs((COL_WIDTH * 2 + COL_SPACING) - USABLE_WIDTH) < 1e-4, "Columns don't sum to usable width"

HEADER_HEIGHT = USABLE_WIDTH * (400.0 / 1600.0)
HEADER_TO_HEADING = 1.0 * cm
HEADING_TO_HR = 0.4 * cm
HR_TO_QA = 0.8 * cm

QA_FONT_SIZE = 8
QA_LEADING = 8.0 # 1.0 line spacing
NUMBER_OFFSET_INSIDE_COL = 0.1 * cm
TEXT_START_INSIDE_COL = 0.7 * cm
LINE_GAP_BETWEEN_ITEMS = 0.1 * cm
MIN_GAP_BETWEEN_QA = 0.5 * cm

HEADING_FONT_SIZE = 12
HR_COLOR = (0.5, 0.5, 0.5)
HR_THICKNESS_PT = 1.0
FOOTER_FONT_SIZE = 11
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)

# ---------- register fonts ----------
def try_register(ttf_path, face_name):
    if os.path.isfile(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont(face_name, ttf_path))
            return True
        except Exception as e:
            print("Font register error:", e)
    return False

alg_ok = try_register(ALGERIAN_TTF, ALG_FACE)
nirmala_ok = try_register(NIRMALA_TTF, NIRMALA_FACE)
badoni_ok  = try_register(BADONI_TTF, BADONI_FACE)
if not alg_ok: ALG_FACE = "Times-Bold"
if not nirmala_ok: NIRMALA_FACE = "Helvetica"
if not badoni_ok: BADONI_FACE = "Times-Roman"

# ---------- NEW: Paragraph styles for both Q & A ----------
question_style = ParagraphStyle(
    name='QuestionStyle',
    fontName=NIRMALA_FACE,
    fontSize=QA_FONT_SIZE,
    leading=QA_LEADING,
    alignment=TA_LEFT,
)

answer_style = ParagraphStyle(
    name='AnswerStyle',
    fontName=NIRMALA_BI_FACE,
    fontSize=QA_FONT_SIZE,
    leading=QA_LEADING,
    alignment=TA_RIGHT,
)

# ---------- content ----------
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

def string_width(text, font_name, font_size):
    return pdfmetrics.stringWidth(text, font_name, font_size)

# ---------- build PDF ----------
OUTFILE = "page1_smart_wrapping.pdf"
c = canvas.Canvas(OUTFILE, pagesize=A4)

# background
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# header, heading, and HR (no changes)
header_x = MARGIN
header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
if os.path.isfile(HEADER_IMAGE):
    c.drawImage(HEADER_IMAGE, header_x, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
else:
    c.setStrokeColorRGB(0.6,0.6,0.6)
    c.rect(header_x, header_y, USABLE_WIDTH, HEADER_HEIGHT)

heading_y = header_y - HEADER_TO_HEADING
heading_text = section_heading.upper()
c.setFont(ALG_FACE, HEADING_FONT_SIZE)
c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, heading_y, heading_text)

hr_y = heading_y - HEADING_TO_HR
c.setStrokeColorRGB(*HR_COLOR)
c.setLineWidth(HR_THICKNESS_PT)
c.line(MARGIN, hr_y, PAGE_WIDTH - MARGIN, hr_y)

# two-column Q&A with new smart logic
start_y = hr_y - HR_TO_QA
current_y = [start_y, start_y]
col_x_start = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
bottom_limit = FOOTER_SECTION_HEIGHT + (0.35 * cm)

col = 0
i = 0
while i < len(qa_lines):
    qa = qa_lines[i]
    
    # Parse into number, question, and answer
    num_part, q_text, a_text = "", qa, ""
    if ' - ' in qa:
        q_part, a_text = qa.split(' - ', 1)
        a_text = "- " + a_text
    else:
        q_part = qa
        
    if '.' in q_part:
        num_part, q_text = q_part.split('.', 1)
        num_part += '.'
    q_text = q_text.strip()

    # Measure widths and define thresholds
    q_width = string_width(q_text, NIRMALA_FACE, QA_FONT_SIZE)
    a_width = string_width(a_text, NIRMALA_BI_FACE, QA_FONT_SIZE) if a_text else 0
    avail_width = COL_WIDTH - TEXT_START_INSIDE_COL
    q_width_threshold = 0.8 * avail_width

    # DECISION: Is this a compact single-line item, or does it need full wrapping?
    use_single_line = (
        q_width <= q_width_threshold and
        (q_width + a_width + MIN_GAP_BETWEEN_QA) <= avail_width
    )

    if use_single_line:
        # --- SCENARIO 1: COMPACT SINGLE-LINE LAYOUT ---
        needed_h = QA_LEADING
        if current_y[col] - needed_h < bottom_limit:
            if col == 0: col = 1; continue
            else: break
        
        y = current_y[col]
        c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
        c.drawString(col_x_start[col] + NUMBER_OFFSET_INSIDE_COL, y, num_part)
        c.drawString(col_x_start[col] + TEXT_START_INSIDE_COL, y, q_text)
        if a_text:
            c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
            c.drawRightString(col_x_start[col] + COL_WIDTH, y, a_text)
        
        current_y[col] -= (needed_h + LINE_GAP_BETWEEN_ITEMS)
        i += 1
    else:
        # --- SCENARIO 2 & 3: ROBUST MULTI-LINE LAYOUT ---
        # Use Paragraphs for both question and answer to handle all wrapping.
        q_para = Paragraph(q_text, question_style)
        a_para = Paragraph(a_text, answer_style) if a_text else None
        
        # Measure required height for both paragraphs
        q_w, q_h = q_para.wrapOn(c, avail_width, PAGE_HEIGHT)
        a_w, a_h = (0, 0)
        if a_para:
            a_w, a_h = a_para.wrapOn(c, avail_width, PAGE_HEIGHT)
        
        needed_h = q_h + a_h
        
        if current_y[col] - needed_h < bottom_limit:
            if col == 0: col = 1; continue
            else: break
            
        y = current_y[col]
        
        # Draw the number, aligned with the baseline of the first line of the question
        c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
        c.drawString(col_x_start[col] + NUMBER_OFFSET_INSIDE_COL, y - QA_LEADING, num_part)

        # Draw the wrapped question paragraph
        # Its bottom-left y-coordinate is y - q_h
        q_para.drawOn(c, col_x_start[col] + TEXT_START_INSIDE_COL, y - q_h)
        
        # Draw the wrapped answer paragraph below the question
        if a_para:
            # Its bottom-left y-coordinate is y - q_h - a_h
            a_para.drawOn(c, col_x_start[col] + TEXT_START_INSIDE_COL, y - q_h - a_h)
        
        current_y[col] -= (needed_h + LINE_GAP_BETWEEN_ITEMS)
        i += 1

# footer
footer_top_y = FOOTER_SECTION_HEIGHT
footer_text_y = footer_top_y - (0.12 * cm)
c.setFont(BADONI_FACE, FOOTER_FONT_SIZE)
c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, footer_text_y, footer_left)
c.drawCentredString(PAGE_WIDTH/2.0, footer_text_y, footer_center)
c.drawRightString(PAGE_WIDTH - MARGIN, footer_text_y, footer_right)

c.showPage()
c.save()
print("Saved:", OUTFILE)