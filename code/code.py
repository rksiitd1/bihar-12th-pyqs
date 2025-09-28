"""
Final, robust two-column generator with a corrected layout engine.

- This version fixes a critical bug where answers could overlap questions in
  multi-line scenarios by using a right-indented paragraph style.
- It restores the space-saving layout where the answer appears on the last line
  of a wrapped question if it fits, without the risk of overlap.
- All layout calculations are performed once and stored, ensuring consistency.
- Line spacing is now uniform between all items, including multi-line Q&A pairs.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import os
import copy # Import the copy module

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
QA_LEADING = 10.0 # 8pt font with 1.25 line spacing
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

# ---------- Paragraph styles for robust wrapping ----------
question_style = ParagraphStyle(name='Question', fontName=NIRMALA_FACE, fontSize=QA_FONT_SIZE, leading=QA_LEADING, alignment=TA_LEFT)
answer_style = ParagraphStyle(name='Answer', fontName=NIRMALA_BI_FACE, fontSize=QA_FONT_SIZE, leading=QA_LEADING, alignment=TA_RIGHT)

# ---------- content ----------
# (Content remains the same)
qa_lines = [
"1. What is the reproductive part of a flowering plant? - The flower.", "2. What is the male part of a flower called? - The Androecium.",
"3. The androecium is made of what units? - Stamens.", "4. A stamen has which two parts? - The anther and the filament.",
"5. What part of the anther makes pollen? - The microsporangium (or pollen sac).", "6. What is the ploidy of a microspore mother cell? - Diploid (2n).",
"7. How do microspore mother cells form microspores? - Through meiosis.", "8. What is the ploidy of a pollen grain? - Haploid (n).",
"9. What is the hard outer layer of pollen? - The exine.", "10. What tough material makes the exine? - Sporopollenin.",
"11. What is the thin inner layer of pollen? - The intine.", "12. Name the two cells in a mature pollen grain. - The vegetative cell and generative cell.",
"13. Which pollen cell is larger and forms the pollen tube? - The vegetative cell.", "14. Which pollen cell forms the two male gametes? - The generative cell.",
"15. What is the female part of a flower called? - The Gynoecium (or pistil).", "16. A pistil has which three parts? - Stigma, style, and ovary.",
"17. Which part of the pistil catches pollen? - The stigma.", "18. What structure is found inside the ovary? - The ovule.",
"19. After fertilization, what does the ovule become? - The seed.", "20. What sac inside the ovule holds the egg cell? - The embryo sac.",
"21. What is the ploidy of a megaspore mother cell? - Diploid (2n).", "22. Meiosis of a megaspore mother cell produces how many megaspores? - Four.",
"23. How many of the four megaspores usually survive? - Only one.", "24. A typical embryo sac has how many cells and nuclei? - 7 cells, 8 nuclei.",
"25. Name the three cells at the micropylar end. - One egg cell and two synergids.", "26. What do we call the egg cell and its two synergids? - The egg apparatus.",
"27. Name the three cells at the opposite (chalazal) end. - The antipodal cells.", "28. What is the large cell in the middle of the embryo sac? - The central cell.",
"29. What two nuclei are in the central cell? - The two polar nuclei.", "30. What is the transfer of pollen to a stigma called? - Pollination.",
"31. Pollination within the same flower is called what? - Autogamy.", "32. Pollination between flowers on the same plant is called what? - Geitonogamy.",
"33. Pollination between flowers on different plants is called what? - Xenogamy.", "34. What is pollination by wind called? - Anemophily.",
"35. What is pollination by insects called? - Entomophily.", "36. What is pollination by water called? - Hydrophily.",
"37. Can the male gametes in flowering plants swim? - No, they are non-motile.", "38. What tube grows from the pollen grain to the ovule? - The pollen tube.",
"39. How many male gametes does the pollen tube deliver? - Two.", "40. What is the fusion of a male gamete and the egg cell? - Syngamy (fertilization).",
"41. Syngamy results in what new cell? - The zygote.", "42. What is a zygote's ploidy? - Diploid (2n).",
"43. What is the second fertilization event in angiosperms? - Triple fusion.", "44. What three nuclei fuse during triple fusion? - One male gamete and two polar nuclei.",
"45. Triple fusion forms what special nucleus? - The Primary Endosperm Nucleus (PEN).", "46. What is the endosperm's ploidy? - Triploid (3n).",
"47. What do we call syngamy and triple fusion happening together? - Double fertilization.", "48. What is the main job of the endosperm? - To feed the growing embryo.",
"49. The zygote grows into what structure? - The embryo.", "50. What part of the ovule becomes the seed coat? - The integuments.",
"51. After fertilization, what does the ovary become? - The fruit.", "52. What do we call a fruit that forms without fertilization? - A parthenocarpic fruit.",
"53. The banana is a natural example of what? - Parthenocarpy.", "54. A fruit that develops only from the ovary is a what? - A true fruit.",
"55. A fruit that develops from more than the ovary is a what? - A false fruit.", "56. The apple is a common example of what kind of fruit? - A false fruit.",
"57. An embryo developing from an unfertilized egg is called what? - Parthenogenesis.", "58. What is it called when seeds form without any fertilization? - Apomixis.",
"59. What do we call it when a single seed has multiple embryos? - Polyembryony.", "60. Polyembryony is common in which type of fruit? - Citrus fruits."
]


# ==============================================================================
# LAYOUT ENGINE CLASS (TRULY CORRECTED)
# ==============================================================================
class LayoutItem:
    def __init__(self, c, num_part, q_text, a_text, avail_width):
        self.c = c
        self.num_part = num_part
        self.q_text = q_text
        self.a_text = a_text
        self.avail_width = avail_width
        self.height = 0
        self.h_q = 0
        self.h_a = 0
        self.layout_type = None
        self.p_q = None
        self.p_a = None
        self._calculate_layout()

    def _get_last_line_width(self, p):
        last_width = 0
        if hasattr(p, 'blPara') and p.blPara:
            for line in reversed(p.blPara.lines):
                if hasattr(line, 'width'):
                    last_width = line.width
                    break
        return last_width

    def _calculate_layout(self):
        q_width = self.c.stringWidth(self.q_text, NIRMALA_FACE, QA_FONT_SIZE)
        a_width = self.c.stringWidth(self.a_text, NIRMALA_BI_FACE, QA_FONT_SIZE) if self.a_text else 0
        QUESTION_WRAP_THRESHOLD = self.avail_width * 0.8

        if q_width < QUESTION_WRAP_THRESHOLD:
            if q_width + a_width + MIN_GAP_BETWEEN_QA <= self.avail_width:
                self.layout_type = 'SINGLE_LINE'
                self.height = QA_LEADING
            else:
                self.layout_type = 'Q_THEN_WRAPPED_A'
                self.p_a = Paragraph(self.a_text, answer_style)
                _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                # --- MODIFIED: Added gap to height calculation for stacked Q&A ---
                self.height = QA_LEADING + LINE_GAP_BETWEEN_ITEMS + self.h_a
        else:
            p_temp = Paragraph(self.q_text, question_style)
            _, h_temp = p_temp.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
            last_line_q_width = self._get_last_line_width(p_temp)

            if self.a_text and (last_line_q_width + MIN_GAP_BETWEEN_QA + a_width) <= self.avail_width:
                self.layout_type = 'WRAPPED_Q_WITH_A_ON_LAST_LINE'
                indent = a_width + MIN_GAP_BETWEEN_QA
                indented_style = copy.copy(question_style)
                indented_style.rightIndent = indent
                self.p_q = Paragraph(self.q_text, indented_style)
                _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height = self.h_q
            else:
                self.layout_type = 'WRAPPED_Q_THEN_WRAPPED_A'
                self.p_q = Paragraph(self.q_text, question_style)
                _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                
                self.h_a = 0
                self.height = self.h_q # Start with question height
                if self.a_text:
                    self.p_a = Paragraph(self.a_text, answer_style)
                    _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                    # --- MODIFIED: Added gap to height calculation for stacked Q&A ---
                    self.height += LINE_GAP_BETWEEN_ITEMS + self.h_a

    def draw(self, x_num, x_text, y_top):
        if self.layout_type == 'SINGLE_LINE':
            baseline = y_top - QA_LEADING
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_num, baseline, self.num_part)
            self.c.drawString(x_text, baseline, self.q_text)
            if self.a_text:
                self.c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
                self.c.drawRightString(x_text + self.avail_width, baseline, self.a_text)
        
        elif self.layout_type == 'Q_THEN_WRAPPED_A':
            q_baseline = y_top - QA_LEADING
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_num, q_baseline, self.num_part)
            self.c.drawString(x_text, q_baseline, self.q_text)
            if self.p_a:
                # The y-coordinate is the *bottom* of the paragraph.
                # Since height now includes the gap, this automatically draws it in the right place.
                self.p_a.drawOn(self.c, x_text, y_top - self.height)

        elif self.layout_type == 'WRAPPED_Q_WITH_A_ON_LAST_LINE':
            num_baseline = y_top - QA_LEADING
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_num, num_baseline, self.num_part)
            self.p_q.drawOn(self.c, x_text, y_top - self.height)
            last_line_baseline = y_top - self.height
            self.c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
            self.c.drawRightString(x_text + self.avail_width, last_line_baseline, self.a_text)
            
        elif self.layout_type == 'WRAPPED_Q_THEN_WRAPPED_A':
            num_baseline = y_top - QA_LEADING
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_num, num_baseline, self.num_part)
            
            y_bottom_q = y_top - self.h_q
            self.p_q.drawOn(self.c, x_text, y_bottom_q)
            
            if self.p_a:
                # --- MODIFIED: Account for the gap when calculating the answer's position ---
                y_bottom_a = y_bottom_q - LINE_GAP_BETWEEN_ITEMS - self.h_a
                self.p_a.drawOn(self.c, x_text, y_bottom_a)

# ==============================================================================
# MAIN SCRIPT
# (No changes needed below this line)
# ==============================================================================
footer_left   = "Page 1 of 13"
footer_center = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
footer_right  = "https://dbggurukulam.com"
section_heading = "Quick revision: One-liner questions and answers"

OUTFILE = "page1_final_architecture_corrected.pdf"
c = canvas.Canvas(OUTFILE, pagesize=A4)
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

# --- Header, Heading, HR ---
header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
if os.path.isfile(HEADER_IMAGE):
    c.drawImage(HEADER_IMAGE, MARGIN, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
else:
    c.setStrokeColorRGB(0.6,0.6,0.6); c.rect(MARGIN, header_y, USABLE_WIDTH, HEADER_HEIGHT)

heading_y = header_y - HEADER_TO_HEADING
c.setFont(ALG_FACE, HEADING_FONT_SIZE); c.setFillColorRGB(0,0,0); c.drawString(MARGIN, heading_y, section_heading.upper())
hr_y = heading_y - HEADING_TO_HR
c.setStrokeColorRGB(*HR_COLOR); c.setLineWidth(HR_THICKNESS_PT); c.line(MARGIN, hr_y, PAGE_WIDTH - MARGIN, hr_y)

# --- Two-Column Q&A with the new Layout Engine ---
start_y = hr_y - HR_TO_QA
current_y = [start_y, start_y]
col_x_starts = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
bottom_limit = FOOTER_SECTION_HEIGHT + (0.35 * cm)
col = 0
i = 0

while i < len(qa_lines):
    qa = qa_lines[i]
    num_part, q_text, a_text = "", qa, ""
    if ' - ' in qa: q_part, a_text = qa.split(' - ', 1); a_text = "- " + a_text
    else: q_part = qa
    if '.' in q_part: num_part, q_text = q_part.split('.', 1); num_part += '.'
    q_text = q_text.strip()
    
    avail_width = COL_WIDTH - TEXT_START_INSIDE_COL
    item = LayoutItem(c, num_part, q_text, a_text, avail_width)
    
    needed_h = item.height + LINE_GAP_BETWEEN_ITEMS
    if current_y[col] - needed_h < bottom_limit:
        if col == 0:
            col = 1
            continue
        else:
            break

    x_num = col_x_starts[col] + NUMBER_OFFSET_INSIDE_COL
    x_text = col_x_starts[col] + TEXT_START_INSIDE_COL
    item.draw(x_num, x_text, current_y[col])
    
    current_y[col] -= needed_h
    i += 1

# --- Footer ---
footer_text_y = FOOTER_SECTION_HEIGHT - (0.12 * cm)
c.setFont(BADONI_FACE, FOOTER_FONT_SIZE); c.setFillColorRGB(0,0,0)
c.drawString(MARGIN, footer_text_y, footer_left)
c.drawCentredString(PAGE_WIDTH/2.0, footer_text_y, footer_center)
c.drawRightString(PAGE_WIDTH - MARGIN, footer_text_y, footer_right)

c.showPage()
c.save()
print("Saved:", OUTFILE)