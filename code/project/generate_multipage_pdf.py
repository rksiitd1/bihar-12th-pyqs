import os
import json
import copy
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT

# ==============================================================================
# --- CONFIGURATION (No changes here) ---
# ==============================================================================

# --- Folders & Output ---
HEADER_FOLDER = "headers"
QNA_FOLDER = "qna"
OUTPUT_FILENAME = "multipage_document_final.pdf"

# --- Static Page Content ---
FOOTER_CENTER_TEXT = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
FOOTER_RIGHT_TEXT = "https://dbggurukulam.com"
SECTION_HEADING_TEXT = "Quick revision: One-liner questions and answers"

# A fixed, explicit PDF document title to show in viewer tabs (e.g., Chrome)
DOCUMENT_TITLE = "Quick Revision – One-liner Q&A | Shri Classes & DBG Gurukulam"

# --- Fonts ---
ALGERIAN_TTF = "Algerian.ttf"
NIRMALA_TTF = "Nirmala.ttf"
BADONI_TTF = "BadoniMT.ttf"

ALG_FACE = "Algerian_Custom"
NIRMALA_FACE = "NirmalaUI_Custom"
BADONI_FACE = "BadoniMT_Custom"
NIRMALA_BI_FACE = "Helvetica-BoldOblique"

# --- Page Layout ---
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm
FOOTER_SECTION_HEIGHT = 1.25 * cm
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

COL_WIDTH = 9.18 * cm
COL_SPACING = 0.1 * cm
assert abs((COL_WIDTH * 2 + COL_SPACING) - USABLE_WIDTH) < 1e-4, "Columns don't sum to usable width"

HEADER_HEIGHT = USABLE_WIDTH * (400.0 / 1600.0)
HEADER_TO_HEADING = 0.8 * cm
HEADING_TO_HR = 0.4 * cm
HR_TO_QA = 0.6 * cm

# --- Typography & Colors ---
QA_FONT_SIZE = 8
QA_LEADING = 9.6
NUMBER_OFFSET_INSIDE_COL = 0.1 * cm
TEXT_START_INSIDE_COL = 0.7 * cm
LINE_GAP_BETWEEN_ITEMS = 0.1 * cm
MIN_GAP_BETWEEN_QA = 0.2 * cm

HEADING_FONT_SIZE = 12
HR_COLOR = (0.5, 0.5, 0.5)
HR_THICKNESS_PT = 1.0
FOOTER_FONT_SIZE = 11
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)


# ==============================================================================
# --- SOPHISTICATED LAYOUT ENGINE (Re-implemented as per your logic) ---
# ==============================================================================
# ==============================================================================
# --- SOPHISTICATED LAYOUT ENGINE (Re-implemented with HYBRID layout) ---
# ==============================================================================
class LayoutItem:
    def __init__(self, c, num_part, q_text, a_text, avail_width):
        self.c = c
        self.num_part = num_part
        self.q_text = q_text
        self.a_text = a_text
        self.avail_width = avail_width
        self.height = 0
        self.h_q = 0 # Height of question part
        self.h_a = 0 # Height of answer part
        self.layout_type = None
        self.p_q = None
        self.p_a = None
        # Store precomputed manual wrapping lines for HYBRID mode to keep
        # calculation and drawing in sync
        self._manual_q_lines = None
        self._calculate_layout()

    def _get_last_line_width(self, p):
        """Safely gets the width of the last line of a wrapped paragraph."""
        if hasattr(p, 'blPara') and p.blPara and p.blPara.lines:
            last_line = p.blPara.lines[-1]
            if hasattr(last_line, 'width'):
                return last_line.width
        return 0

    def _calculate_layout(self):
        question_style = ParagraphStyle(name='Question', fontName=NIRMALA_FACE, fontSize=QA_FONT_SIZE, leading=QA_LEADING)
        answer_style = ParagraphStyle(name='Answer', fontName=NIRMALA_BI_FACE, fontSize=QA_FONT_SIZE, leading=QA_LEADING, alignment=TA_RIGHT)

        q_width = self.c.stringWidth(self.q_text, NIRMALA_FACE, QA_FONT_SIZE)
        a_width = self.c.stringWidth(self.a_text, NIRMALA_BI_FACE, QA_FONT_SIZE) if self.a_text else 0
        
        # Heuristic: If question is short, check for single-line possibilities
        if q_width < self.avail_width * 1.0:
            # Path 1: Perfect single-line fit
            if q_width + a_width + MIN_GAP_BETWEEN_QA <= self.avail_width:
                self.layout_type = 'SINGLE_LINE'
                self.height = QA_LEADING
                return
            else:
                # Path 2: Question is single line, but answer wraps below
                self.layout_type = 'Q_THEN_WRAPPED_A'
                self.h_q = QA_LEADING
                self.p_a = Paragraph(self.a_text, answer_style)
                _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height = self.h_q + LINE_GAP_BETWEEN_ITEMS + self.h_a
                return

        # Path 3 & 4: Question itself must be wrapped
        # IMPORTANT: Use the SAME manual wrapping as the draw method so the
        # last line width used for HYBRID decision matches exactly.
        words = self.q_text.split()
        manual_lines = []
        current_line = ""
        for word in words:
            sep = " " if current_line else ""
            test_line = current_line + sep + word
            if self.c.stringWidth(test_line, NIRMALA_FACE, QA_FONT_SIZE) <= self.avail_width:
                current_line = test_line
            else:
                if current_line:
                    manual_lines.append(current_line)
                current_line = word
        if current_line:
            manual_lines.append(current_line)

        # Height of the wrapped question when drawn line-by-line
        h_manual_q = len(manual_lines) * QA_LEADING if manual_lines else 0
        last_line_q_width = self.c.stringWidth(manual_lines[-1], NIRMALA_FACE, QA_FONT_SIZE) if manual_lines else 0

        # Path 3 (HYBRID): Answer fits on the last line of the MANUALLY wrapped question
        if self.a_text and manual_lines and (last_line_q_width + MIN_GAP_BETWEEN_QA + a_width) <= self.avail_width:
            self.layout_type = 'HYBRID_A_ON_LAST_LINE'
            self.height = h_manual_q
            self._manual_q_lines = manual_lines
        else:
            # Path 4: Fully stacked layout where both Q and A can wrap independently
            self.layout_type = 'WRAPPED_Q_THEN_WRAPPED_A'
            self.p_q = Paragraph(self.q_text, question_style)
            _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
            self.height = self.h_q
            if self.a_text:
                self.p_a = Paragraph(self.a_text, answer_style)
                _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height += LINE_GAP_BETWEEN_ITEMS + self.h_a

    def _draw_hybrid_layout(self, x_text, y_top):
        """Manually wraps and draws text to allow full width on all but the last line."""
        
        # We rely on precomputed lines from _calculate_layout to guarantee
        # consistency between the layout decision and drawing.
        lines = self._manual_q_lines or []
        if not lines:
            return

        # 2. Draw the lines one by one
        num_lines = len(lines)
        for i, line_text in enumerate(lines):
            is_last_line = (i == num_lines - 1)
            y_baseline = y_top - (i * QA_LEADING) - QA_LEADING

            # Draw the question part for the current line
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_text, y_baseline, line_text)

            # If it's the last line, also draw the answer
            if is_last_line and self.a_text:
                self.c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
                self.c.drawRightString(x_text + self.avail_width, y_baseline, self.a_text)

    def draw(self, x_num, x_text, y_top):
        # Draw the number, consistent for all layouts
        num_baseline = y_top - QA_LEADING
        self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
        self.c.drawString(x_num, num_baseline, self.num_part)

        if self.layout_type == 'SINGLE_LINE':
            self.c.drawString(x_text, num_baseline, self.q_text)
            if self.a_text:
                self.c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
                self.c.drawRightString(x_text + self.avail_width, num_baseline, self.a_text)
        
        elif self.layout_type == 'Q_THEN_WRAPPED_A':
            self.c.drawString(x_text, num_baseline, self.q_text)
            if self.p_a:
                y_a_bottom = y_top - self.h_q - LINE_GAP_BETWEEN_ITEMS - self.h_a
                self.p_a.drawOn(self.c, x_text, y_a_bottom)

        elif self.layout_type == 'HYBRID_A_ON_LAST_LINE':
            # Use our new custom drawing function for this specific case
            self._draw_hybrid_layout(x_text, y_top)
            
        elif self.layout_type == 'WRAPPED_Q_THEN_WRAPPED_A':
            # Draw the question paragraph.
            y_question_bottom = y_top - self.h_q
            self.p_q.drawOn(self.c, x_text, y_question_bottom)
            
            if self.p_a:
                # THIS IS THE FIX
                # Calculate the answer's position directly from the original y_top.
                # This prevents any cascading errors from the question's position calculation.
                y_answer_bottom = y_top - self.h_q - LINE_GAP_BETWEEN_ITEMS - self.h_a
                self.p_a.drawOn(self.c, x_text, y_answer_bottom)


# ==============================================================================
# --- PDF GENERATOR CLASS (No changes here) ---
# ==============================================================================
class PdfGenerator:
    def __init__(self, output_filename, total_pages, doc_title: str | None = None):
        self.c = canvas.Canvas(output_filename, pagesize=A4)
        self.total_pages = total_pages
        self._register_fonts()
        # Set a browser/tab title (PDF metadata Title) for viewers like Chrome
        if doc_title:
            try:
                self.c.setTitle(doc_title)
            except Exception:
                # Fail silently if any environment does not support setting title
                pass

    def _register_fonts(self):
        global ALG_FACE, NIRMALA_FACE, BADONI_FACE
        if not self._try_register(ALGERIAN_TTF, ALG_FACE): ALG_FACE = "Times-Bold"
        if not self._try_register(NIRMALA_TTF, NIRMALA_FACE): NIRMALA_FACE = "Helvetica"
        if not self._try_register(BADONI_TTF, BADONI_FACE): BADONI_FACE = "Times-Roman"

    def _try_register(self, ttf_path, face_name):
        if os.path.isfile(ttf_path):
            try:
                pdfmetrics.registerFont(TTFont(face_name, ttf_path))
                return True
            except Exception as e: print(f"Font register error for {ttf_path}: {e}")
        return False

    def draw_page(self, page_number, header_image_path, qna_data):
        self.c.setFillColorRGB(*PAGE_BG_RGB)
        self.c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
        if os.path.isfile(header_image_path):
            self.c.drawImage(header_image_path, MARGIN, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
        else:
            print(f"Warning: Header image not found at '{header_image_path}'")
            self.c.setStrokeColorRGB(0.6,0.6,0.6); self.c.rect(MARGIN, header_y, USABLE_WIDTH, HEADER_HEIGHT)
        heading_y = header_y - HEADER_TO_HEADING
        self.c.setFont(ALG_FACE, HEADING_FONT_SIZE); self.c.setFillColorRGB(0,0,0)
        self.c.drawString(MARGIN, heading_y, SECTION_HEADING_TEXT.upper())
        hr_y = heading_y - HEADING_TO_HR
        self.c.setStrokeColorRGB(*HR_COLOR); self.c.setLineWidth(HR_THICKNESS_PT)
        self.c.line(MARGIN, hr_y, PAGE_WIDTH - MARGIN, hr_y)
        self._draw_qna_columns(hr_y - HR_TO_QA, qna_data)
        footer_text_y = FOOTER_SECTION_HEIGHT - (0.12 * cm)
        footer_left_text = f"Page {page_number} of {self.total_pages}"
        self.c.setFont(BADONI_FACE, FOOTER_FONT_SIZE); self.c.setFillColorRGB(0,0,0)
        self.c.drawString(MARGIN, footer_text_y, footer_left_text)
        self.c.drawCentredString(PAGE_WIDTH/2.0, footer_text_y, FOOTER_CENTER_TEXT)
        self.c.drawRightString(PAGE_WIDTH - MARGIN, footer_text_y, FOOTER_RIGHT_TEXT)
        self.c.showPage()
        print(f"Successfully generated Page {page_number}.")

    def _draw_qna_columns(self, start_y, qna_items):
        current_y = [start_y, start_y]
        col_x_starts = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
        bottom_limit = FOOTER_SECTION_HEIGHT + (0.60 * cm)
        col = 0
        question_number_counter = 1
        i = 0
        while i < len(qna_items):
            item_data = qna_items[i]
            q_text = item_data.get("q", "Missing question").strip()
            a_raw = item_data.get("a", "")
            num_part = f"{question_number_counter}."
            a_text = f"- {a_raw.strip()}" if a_raw else ""
            
            # This is the available width for the text paragraph itself
            avail_width = COL_WIDTH - TEXT_START_INSIDE_COL
            item = LayoutItem(self.c, num_part, q_text, a_text, avail_width)
            
            needed_h = item.height + LINE_GAP_BETWEEN_ITEMS
            if current_y[col] - needed_h < bottom_limit:
                if col == 0:
                    col = 1; continue
                else:
                    print(f"Warning: Content overflow. Item '{num_part} {q_text[:30]}...' could not fit.")
                    break
            
            # Calculate the separate x-coordinates for number and text
            x_num = col_x_starts[col] + NUMBER_OFFSET_INSIDE_COL
            x_text = col_x_starts[col] + TEXT_START_INSIDE_COL
            item.draw(x_num, x_text, current_y[col])
            
            current_y[col] -= needed_h
            question_number_counter += 1
            i += 1

    def save(self):
        self.c.save()
        print(f"\nPDF saved as '{OUTPUT_FILENAME}'")

# ==============================================================================
# --- MAIN EXECUTION (No changes here) ---
# ==============================================================================
def main():
    if not os.path.isdir(HEADER_FOLDER) or not os.path.isdir(QNA_FOLDER):
        print(f"Error: Required folders '{HEADER_FOLDER}' and/or '{QNA_FOLDER}' not found."); return
    try:
        # Use a natural sort key so files like header1.png, header2.png, header10.png
        # are ordered numerically (1,2,10) instead of lexicographically (1,10,2).
        def _numeric_key(fn: str):
            name = os.path.splitext(fn)[0]
            # Try to extract trailing integer from the base name, e.g. 'header12' -> 12
            # If not present, fall back to 0 and then the full name to stabilize order.
            import re
            m = re.search(r"(\d+)$", name)
            if m:
                return (int(m.group(1)), name)
            return (0, name)

        header_files = sorted(
            [f for f in os.listdir(HEADER_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
            key=_numeric_key
        )
        num_pages = len(header_files)
    except OSError as e:
        print(f"Error reading header directory '{HEADER_FOLDER}': {e}"); return
    if num_pages == 0:
        print(f"No header images found in '{HEADER_FOLDER}'.")
    else:
        # Use a fixed, predefined document title (no JSON inference)
        pdf = PdfGenerator(OUTPUT_FILENAME, num_pages, DOCUMENT_TITLE)
        for i, header_filename in enumerate(header_files, 1):
            page_number = i
            base_name = os.path.splitext(header_filename)[0]
            page_name = base_name.replace('header', 'page', 1)
            qna_path = os.path.join(QNA_FOLDER, f"{page_name}.json")
            header_path = os.path.join(HEADER_FOLDER, header_filename)
            if not os.path.isfile(qna_path):
                print(f"Warning: Skipping page {page_number}. Q&A file '{qna_path}' not found."); continue
            try:
                with open(qna_path, 'r', encoding='utf-8') as f:
                    qna_data = json.load(f)
                if not isinstance(qna_data, list):
                    print(f"Error: JSON in '{qna_path}' is not a list. Skipping page."); continue
                pdf.draw_page(page_number, header_path, qna_data)
            except json.JSONDecodeError:
                print(f"Error: Could not parse JSON from '{qna_path}'. Skipping page.")
            except Exception as e:
                import traceback
                print(f"An unexpected error occurred while processing page {page_number}: {e}")
                traceback.print_exc()
        pdf.save()

if __name__ == "__main__":
    main()