import os
import re
import json
import copy
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_JUSTIFY

# ==============================================================================
# --- CONFIGURATION (No changes here) ---
# ==============================================================================

# --- Folders & Output ---
HEADER_FOLDER = "headers"
QNA_FOLDER = "qna"
SHORTS_FOLDER = "shorts"
OUTPUT_FILENAME = "multipage_document_final.pdf"
WATERMARK_PATH = "logo.png"
WATERMARK_ALPHA = 0.2
WATERMARK_REL_WIDTH = 0.5
WATERMARK_ENABLED = False

# --- Static Page Content ---
FOOTER_CENTER_TEXT = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
FOOTER_RIGHT_TEXT = "https://dbggurukulam.com"
SECTION_HEADING_TEXT = "Quick revision: One-liner questions and answers"
EVEN_SECTION_HEADING_TEXT = "Important questions and answers"
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
        self.q_img = None
        self.q_img_h = 0
        self.a_img = None
        self.a_img_h = 0
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

        has_complex_math_q = '$' in self.q_text
        has_complex_math_a = '$' in self.a_text
        has_simple_markup_q = any(m in self.q_text for m in ['\\', '<sup', '<sub'])
        has_simple_markup_a = any(m in self.a_text for m in ['\\', '<sup', '<sub'])

        if has_complex_math_q or has_complex_math_a or has_simple_markup_q or has_simple_markup_a:
            self.layout_type = 'WRAPPED_Q_THEN_WRAPPED_A'
            if has_complex_math_q:
                img_info = self._render_text_block_to_image(self.q_text, bold=False)
                if img_info:
                    self.q_img, self.q_img_h = img_info; self.h_q = self.q_img_h
            if not self.h_q:
                q_markup = self._convert_simple_latex_to_markup(self.q_text)
                self.p_q = Paragraph(q_markup, question_style)
                _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
            self.height = self.h_q
            
            if self.a_text:
                if has_complex_math_a:
                    img_info = self._render_text_block_to_image(self.a_text, bold=False)
                    if img_info:
                        self.a_img, self.a_img_h = img_info; self.h_a = self.a_img_h
                if not self.h_a:
                    a_markup = self._convert_simple_latex_to_markup(self.a_text)
                    self.p_a = Paragraph(a_markup, answer_style)
                    _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height += LINE_GAP_BETWEEN_ITEMS + self.h_a
            return

        q_width = self.c.stringWidth(self.q_text, NIRMALA_FACE, QA_FONT_SIZE)
        a_width = self.c.stringWidth(self.a_text, NIRMALA_BI_FACE, QA_FONT_SIZE) if self.a_text else 0
        
        if q_width < self.avail_width * 1.0:
            if q_width + a_width + MIN_GAP_BETWEEN_QA <= self.avail_width:
                self.layout_type = 'SINGLE_LINE'
                self.height = QA_LEADING
                return
            else:
                self.layout_type = 'Q_THEN_WRAPPED_A'
                self.h_q = QA_LEADING
                self.p_a = Paragraph(self.a_text, answer_style)
                _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height = self.h_q + LINE_GAP_BETWEEN_ITEMS + self.h_a
                return

        words = self.q_text.split()
        manual_lines = []
        current_line = ""
        for word in words:
            sep = " " if current_line else ""
            test_line = current_line + sep + word
            if self.c.stringWidth(test_line, NIRMALA_FACE, QA_FONT_SIZE) <= self.avail_width:
                current_line = test_line
            else:
                if current_line: manual_lines.append(current_line)
                current_line = word
        if current_line: manual_lines.append(current_line)

        h_manual_q = len(manual_lines) * QA_LEADING if manual_lines else 0
        last_line_q_width = self.c.stringWidth(manual_lines[-1], NIRMALA_FACE, QA_FONT_SIZE) if manual_lines else 0

        if self.a_text and manual_lines and (last_line_q_width + MIN_GAP_BETWEEN_QA + a_width) <= self.avail_width:
            self.layout_type = 'HYBRID_A_ON_LAST_LINE'
            self.height = h_manual_q
            self._manual_q_lines = manual_lines
        else:
            self.layout_type = 'WRAPPED_Q_THEN_WRAPPED_A'
            self.p_q = Paragraph(self.q_text, question_style)
            _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
            self.height = self.h_q
            if self.a_text:
                self.p_a = Paragraph(self.a_text, answer_style)
                _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)
                self.height += LINE_GAP_BETWEEN_ITEMS + self.h_a

    def _draw_hybrid_layout(self, x_text, y_top):
        lines = self._manual_q_lines or []
        if not lines: return

        num_lines = len(lines)
        for i, line_text in enumerate(lines):
            is_last_line = (i == num_lines - 1)
            y_baseline = y_top - (i * QA_LEADING) - QA_LEADING
            self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
            self.c.drawString(x_text, y_baseline, line_text)
            if is_last_line and self.a_text:
                self.c.setFont(NIRMALA_BI_FACE, QA_FONT_SIZE)
                self.c.drawRightString(x_text + self.avail_width, y_baseline, self.a_text)

    def draw(self, x_num, x_text, y_top):
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
            self._draw_hybrid_layout(x_text, y_top)
            
        elif self.layout_type == 'WRAPPED_Q_THEN_WRAPPED_A':
            y_question_bottom = y_top - self.h_q
            if self.q_img:
                self.c.drawImage(self.q_img, x_text, y_question_bottom, width=self.avail_width, height=self.h_q, preserveAspectRatio=True, mask='auto')
            else:
                self.p_q.drawOn(self.c, x_text, y_question_bottom)
            
            if self.p_a or self.a_img:
                y_answer_bottom = y_top - self.h_q - LINE_GAP_BETWEEN_ITEMS - self.h_a
                if self.a_img:
                    self.c.drawImage(self.a_img, x_text, y_answer_bottom, width=self.avail_width, height=self.h_a, preserveAspectRatio=True, mask='auto')
                else:
                    self.p_a.drawOn(self.c, x_text, y_answer_bottom)

    def _render_text_block_to_image(self, text: str, bold: bool = False):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib import rcParams
            from PIL import Image
            import tempfile
        except ImportError:
            print("Warning: Matplotlib or Pillow not installed. Cannot render LaTeX.")
            return None

        try:
            # Configure matplotlib for clean text rendering
            rcParams['mathtext.fontset'] = 'dejavusans'
            rcParams['font.family'] = 'sans-serif'
            
            weight = 'bold' if bold else 'normal'
            fig_w_inches = self.avail_width / 72.0
            dpi = 300

            fig = plt.figure(figsize=(fig_w_inches, 1), dpi=dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            
            # Matplotlib's default text rendering engine (mathtext) will parse '$...$'
            ax.text(0, 1, text, fontsize=QA_FONT_SIZE, fontweight=weight, va='top', ha='left', wrap=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp_path = tmp.name
            
            fig.savefig(tmp_path, dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0.01)
            plt.close(fig)

            with Image.open(tmp_path) as im:
                px_w, px_h = im.size
                # Convert pixel height back to PDF points
                height_in_points = px_h * 72.0 / dpi
            
            return (tmp_path, height_in_points)
        except Exception as e:
            print(f"Error during matplotlib rendering: {e}")
            try:
                plt.close('all')
            except Exception:
                pass
            return None

    def _convert_simple_latex_to_markup(self, text: str) -> str:
        if not text: return ""
        out = text.replace('\\\\', '<br/>').replace('\\n', '<br/>')
        out = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", out)
        out = re.sub(r"\\textsuperscript\{([^}]*)\}", r"<super>\1</super>", out)
        out = re.sub(r"<\s*sup\s*>\s*(.*?)\s*<\s*/\s*sup\s*>", r"<super>\1</super>", out, flags=re.IGNORECASE)
        out = re.sub(r"\\textsubscript\{([^}]*)\}", r"<sub>\1</sub>", out)
        out = re.sub(r"<\s*sub\s*>\s*(.*?)\s*<\s*/\s*sub\s*>", r"<sub>\1</sub>", out, flags=re.IGNORECASE)
        return out

class ShortLayoutItem:
    def __init__(self, c, num_part, q_text, a_text, avail_width):
        self.c = c
        self.num_part = num_part
        self.q_text = q_text
        self.a_text = a_text or ""
        self.avail_width = avail_width
        self.height = 0
        self.h_q = 0
        self.h_a = 0
        self.p_q = None
        self.p_a = None
        self.q_img = None
        self.q_img_h = 0
        self.a_img = None
        self.a_img_h = 0
        self._calculate()

    def _calculate(self):
        question_style = ParagraphStyle(name='ShortsQ', fontName="Helvetica-Bold", fontSize=QA_FONT_SIZE, leading=QA_LEADING, alignment=TA_JUSTIFY)
        answer_style = ParagraphStyle(name='ShortsA', fontName="Helvetica", fontSize=QA_FONT_SIZE, leading=QA_LEADING, alignment=TA_JUSTIFY)

        has_complex_math_q = '$' in self.q_text
        has_complex_math_a = '$' in self.a_text

        q_text_conv = self._convert_simple_latex_to_markup(self.q_text)
        a_text_conv = self._convert_simple_latex_to_markup(self.a_text)

        if has_complex_math_q:
            img_info = self._render_text_block_to_image(self.q_text, bold=True)
            if img_info:
                self.q_img, self.q_img_h = img_info; self.h_q = self.q_img_h
        if not self.h_q:
            self.p_q = Paragraph(q_text_conv, question_style)
            _, self.h_q = self.p_q.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)

        if has_complex_math_a:
            img_info = self._render_text_block_to_image(self.a_text, bold=False)
            if img_info:
                self.a_img, self.a_img_h = img_info; self.h_a = self.a_img_h
        if not self.h_a and self.a_text:
            self.p_a = Paragraph(a_text_conv, answer_style)
            _, self.h_a = self.p_a.wrapOn(self.c, self.avail_width, PAGE_HEIGHT)

        self.height = self.h_q + LINE_GAP_BETWEEN_ITEMS + self.h_a

    def draw(self, x_num, x_text, y_top):
        num_baseline = y_top - QA_LEADING
        self.c.setFont(NIRMALA_FACE, QA_FONT_SIZE)
        self.c.drawString(x_num, num_baseline, self.num_part)

        y_q_bottom = y_top - self.h_q
        if self.q_img:
            self.c.drawImage(self.q_img, x_text, y_q_bottom, width=self.avail_width, height=self.h_q, preserveAspectRatio=True, mask='auto')
        else:
            self.p_q.drawOn(self.c, x_text, y_q_bottom)

        if self.a_text:
            y_a_bottom = y_q_bottom - LINE_GAP_BETWEEN_ITEMS - self.h_a
            if self.a_img:
                self.c.drawImage(self.a_img, x_text, y_a_bottom, width=self.avail_width, height=self.h_a, preserveAspectRatio=True, mask='auto')
            else:
                self.p_a.drawOn(self.c, x_text, y_a_bottom)

    # ** THIS IS THE MAIN FIX **
    # Using the same robust rendering function as the LayoutItem class.
    def _render_text_block_to_image(self, text: str, bold: bool = False):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib import rcParams
            from PIL import Image
            import tempfile
        except ImportError:
            print("Warning: Matplotlib or Pillow not installed. Cannot render LaTeX.")
            return None

        try:
            # Configure matplotlib for clean text rendering
            rcParams['mathtext.fontset'] = 'dejavusans'
            rcParams['font.family'] = 'sans-serif'
            
            weight = 'bold' if bold else 'normal'
            fig_w_inches = self.avail_width / 72.0
            dpi = 300

            fig = plt.figure(figsize=(fig_w_inches, 1), dpi=dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            
            # Matplotlib's default text rendering engine (mathtext) will parse '$...$'
            ax.text(0, 1, text, fontsize=QA_FONT_SIZE, fontweight=weight, va='top', ha='left', wrap=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp_path = tmp.name
            
            fig.savefig(tmp_path, dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0.01)
            plt.close(fig)

            with Image.open(tmp_path) as im:
                px_w, px_h = im.size
                # Convert pixel height back to PDF points
                height_in_points = px_h * 72.0 / dpi
            
            return (tmp_path, height_in_points)
        except Exception as e:
            print(f"Error during matplotlib rendering: {e}")
            try:
                plt.close('all')
            except Exception:
                pass
            return None

    def _convert_simple_latex_to_markup(self, text: str) -> str:
        if not text: return ""
        out = text.replace('\\\\', '<br/>').replace('\\n', '<br/>')
        out = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", out)
        out = re.sub(r"\\textsuperscript\{([^}]*)\}", r"<super>\1</super>", out)
        out = re.sub(r"<\s*sup\s*>\s*(.*?)\s*<\s*/\s*sup\s*>", r"<super>\1</super>", out, flags=re.IGNORECASE)
        out = re.sub(r"\\textsubscript\{([^}]*)\}", r"<sub>\1</sub>", out)
        out = re.sub(r"<\s*sub\s*>\s*(.*?)\s*<\s*/\s*sub\s*>", r"<sub>\1</sub>", out, flags=re.IGNORECASE)
        return out

# ==============================================================================
# --- PDF GENERATOR CLASS (No changes here) ---
# ==============================================================================
class PdfGenerator:
    def __init__(self, output_filename, total_pages, doc_title: str | None = None):
        self.c = canvas.Canvas(output_filename, pagesize=A4)
        self.total_pages = total_pages
        self._register_fonts()
        if doc_title:
            try:
                self.c.setTitle(doc_title)
            except Exception:
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

    def draw_page(self, page_number, header_image_path, qna_data, section_heading_text: str, *, use_header_image: bool, layout_mode: str):
        self.c.setFillColorRGB(*PAGE_BG_RGB)
        self.c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        if WATERMARK_ENABLED: self._draw_watermark()
        
        header_y = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
        if layout_mode == 'odd' and use_header_image:
            if os.path.isfile(header_image_path):
                self.c.drawImage(header_image_path, MARGIN, header_y, width=USABLE_WIDTH, height=HEADER_HEIGHT, preserveAspectRatio=True)
            else:
                print(f"Warning: Header image not found at '{header_image_path}'")
                self.c.setStrokeColorRGB(0.6,0.6,0.6); self.c.rect(MARGIN, header_y, USABLE_WIDTH, HEADER_HEIGHT)

        heading_y = (PAGE_HEIGHT - MARGIN - HEADER_TO_HEADING) if layout_mode == 'even' else (header_y - HEADER_TO_HEADING)
        self.c.setFont(ALG_FACE, HEADING_FONT_SIZE); self.c.setFillColorRGB(0,0,0)
        self.c.drawString(MARGIN, heading_y, section_heading_text.upper())
        hr_y = heading_y - HEADING_TO_HR
        self.c.setStrokeColorRGB(*HR_COLOR); self.c.setLineWidth(HR_THICKNESS_PT)
        self.c.line(MARGIN, hr_y, PAGE_WIDTH - MARGIN, hr_y)
        self._draw_qna_columns(hr_y - HR_TO_QA, qna_data, layout_mode)
        
        footer_text_y = FOOTER_SECTION_HEIGHT - (0.12 * cm)
        footer_left_text = f"Page {page_number} of {self.total_pages}"
        self.c.setFont(BADONI_FACE, FOOTER_FONT_SIZE); self.c.setFillColorRGB(0,0,0)
        self.c.drawString(MARGIN, footer_text_y, footer_left_text)
        self.c.drawCentredString(PAGE_WIDTH/2.0, footer_text_y, FOOTER_CENTER_TEXT)
        self.c.drawRightString(PAGE_WIDTH - MARGIN, footer_text_y, FOOTER_RIGHT_TEXT)
        self.c.showPage()
        print(f"Successfully generated Page {page_number}.")

    def _draw_watermark(self):
        if not os.path.isfile(WATERMARK_PATH): return
        target_w = USABLE_WIDTH * WATERMARK_REL_WIDTH
        target_h = target_w
        x = (PAGE_WIDTH - target_w) / 2.0
        y = (PAGE_HEIGHT - target_h) / 2.0
        self.c.saveState()
        try:
            self.c.setFillAlpha(WATERMARK_ALPHA)
            self.c.setStrokeAlpha(WATERMARK_ALPHA)
        except Exception: pass
        self.c.drawImage(WATERMARK_PATH, x, y, width=target_w, height=target_h, preserveAspectRatio=True, mask='auto')
        self.c.restoreState()

    def _draw_qna_columns(self, start_y, qna_items, layout_mode: str):
        current_y = [start_y, start_y]
        col_x_starts = [MARGIN, MARGIN + COL_WIDTH + COL_SPACING]
        bottom_limit = FOOTER_SECTION_HEIGHT + (0.60 * cm)
        col = 0
        question_number_counter = 1
        i = 0
        all_rendered_images = []

        while i < len(qna_items):
            item_data = qna_items[i]
            q_text = item_data.get("q", "Missing question").strip()
            a_raw = item_data.get("a", "")
            num_part = f"{question_number_counter}."
            a_text = f"- {a_raw.strip()}" if layout_mode == 'odd' and a_raw else a_raw.strip()
            
            avail_width = COL_WIDTH - TEXT_START_INSIDE_COL
            item = LayoutItem(self.c, num_part, q_text, a_text, avail_width) if layout_mode == 'odd' else ShortLayoutItem(self.c, num_part, q_text, a_text, avail_width)
            
            needed_h = item.height + LINE_GAP_BETWEEN_ITEMS
            if current_y[col] - needed_h < bottom_limit:
                if col == 0:
                    col = 1; continue
                else:
                    print(f"Warning: Content overflow. Item '{num_part} {q_text[:30]}...' could not fit.")
                    break
            
            x_num = col_x_starts[col] + NUMBER_OFFSET_INSIDE_COL
            x_text = col_x_starts[col] + TEXT_START_INSIDE_COL
            item.draw(x_num, x_text, current_y[col])
            
            # Keep track of temporary image files to delete later
            if item.q_img: all_rendered_images.append(item.q_img)
            if item.a_img: all_rendered_images.append(item.a_img)

            current_y[col] -= needed_h
            question_number_counter += 1
            i += 1
        
        # Clean up all temporary image files created for this page
        for img_path in all_rendered_images:
            try:
                os.remove(img_path)
            except OSError:
                pass

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
        def _numeric_key(fn: str):
            name = os.path.splitext(fn)[0]
            m = re.search(r"(\d+)$", name)
            return (int(m.group(1)), name) if m else (0, name)

        header_files = sorted([f for f in os.listdir(HEADER_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))], key=_numeric_key)
        num_pages = len(header_files) * 2
    except OSError as e:
        print(f"Error reading header directory '{HEADER_FOLDER}': {e}"); return
    
    if num_pages == 0:
        print(f"No header images found in '{HEADER_FOLDER}'.")
        return

    pdf = PdfGenerator(OUTPUT_FILENAME, num_pages, DOCUMENT_TITLE)
    for i, header_filename in enumerate(header_files, 1):
        base_name = os.path.splitext(header_filename)[0]
        page_name = base_name.replace('header', 'page', 1)
        header_path = os.path.join(HEADER_FOLDER, header_filename)

        # 1) ODD page (front)
        odd_page_number = 2 * i - 1
        try:
            qna_path_front = os.path.join(QNA_FOLDER, f"{page_name}.json")
            if not os.path.isfile(qna_path_front):
                print(f"Warning: Skipping odd page {odd_page_number}. Q&A file '{qna_path_front}' not found.")
            else:
                with open(qna_path_front, 'r', encoding='utf-8') as f: qna_data_front = json.load(f)
                if isinstance(qna_data_front, list):
                    pdf.draw_page(odd_page_number, header_path, qna_data_front, SECTION_HEADING_TEXT, use_header_image=True, layout_mode='odd')
                else:
                    print(f"Error: JSON in '{qna_path_front}' is not a list. Skipping odd page {odd_page_number}.")
        except Exception as e:
            import traceback; print(f"An unexpected error occurred while processing odd page {odd_page_number}: {e}"); traceback.print_exc()

        # 2) EVEN page (back)
        even_page_number = 2 * i
        try:
            candidates = [
                os.path.join(SHORTS_FOLDER, f"{page_name}.json"),
                os.path.join(SHORTS_FOLDER, f"page{odd_page_number}.json"),
                os.path.join(SHORTS_FOLDER, f"page{even_page_number}.json"),
                os.path.join(SHORTS_FOLDER, f"ch{i}.json"),
            ]
            qna_path_back = next((p for p in candidates if os.path.isfile(p)), None)
            if not qna_path_back:
                print(f"Warning: Skipping even page {even_page_number}. No shorts Q&A file found for chapter {i}.")
                continue

            with open(qna_path_back, 'r', encoding='utf-8') as f: qna_data_back = json.load(f)
            if isinstance(qna_data_back, list):
                pdf.draw_page(even_page_number, header_path, qna_data_back, EVEN_SECTION_HEADING_TEXT, use_header_image=False, layout_mode='even')
            else:
                print(f"Error: JSON in '{qna_path_back}' is not a list. Skipping even page {even_page_number}.")
        except Exception as e:
            import traceback; print(f"An unexpected error occurred while processing even page {even_page_number}: {e}"); traceback.print_exc()
    
    pdf.save()

if __name__ == "__main__":
    main()