from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# -------------------------
# Page / layout constants
# -------------------------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm            # top, bottom, left, right
FOOTER_BASELINE = 1.25 * cm   # footer baseline measured from bottom
HEADER_IMAGE = "header.png"   # place your 1600x400 px header here
HEADER_PIXELS = (1600, 400)   # used to keep aspect ratio (4:1)

# Fonts & sizes (close match to original)
TITLE_FONT = "Times-Roman"
BOLD_FONT = "Times-Bold"
TITLE_SIZE = 11
HEADING_SIZE = 12
BODY_SIZE = 11
LINE_LEADING = 14

# -------------------------
# Compute header dimensions (keeps 4:1 ratio)
# -------------------------
usable_width = PAGE_WIDTH - 2 * MARGIN
header_height = usable_width * (HEADER_PIXELS[1] / HEADER_PIXELS[0])  # = width * 0.25

# small vertical gap under header
GAP_AFTER_HEADER = 0.25 * cm

# -------------------------
# Text content (first page)
# -------------------------
# (I copied the exact lines from your uploaded first page; extend if needed)
title_line = "Page 1 of 13   Shri Classes & DBG Gurukulam (by IITian Golu Sir)   https://dbggurukulam.com"
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
# (continue to include all lines up to the part that belongs to page 1)
]

footer_text = "Shri Classes & DBG Gurukulam (by IITian Golu Sir) — https://dbggurukulam.com"

# -------------------------
# Build PDF
# -------------------------
pdf_out = "page1_exact_repro.pdf"
c = canvas.Canvas(pdf_out, pagesize=A4)

# Draw header image at top inside margins
header_x = MARGIN
header_y = PAGE_HEIGHT - MARGIN - header_height
try:
    c.drawImage(HEADER_IMAGE, header_x, header_y, width=usable_width, height=header_height, preserveAspectRatio=True)
except Exception as e:
    # If header image missing, draw placeholder box (so layout still matches)
    c.setStrokeColorRGB(0.6,0.6,0.6)
    c.rect(header_x, header_y, usable_width, header_height)
    c.setFont(TITLE_FONT, 9)
    c.drawCentredString(header_x + usable_width/2, header_y + header_height/2, "HEADER IMAGE MISSING: put header.png here")

# Title line: place directly under header with same single-line layout and spacing between segments
title_y = header_y - GAP_AFTER_HEADER - (0.2 * cm)  # small nudge down
c.setFont(TITLE_FONT, TITLE_SIZE)
# We'll render as three "columns": left, center, right to match spacing in original
left_text = "Page 1 of 13"
center_text = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
right_text = "https://dbggurukulam.com"
# positions
left_x = MARGIN
center_x = PAGE_WIDTH / 2
right_x = PAGE_WIDTH - MARGIN
# draw
c.drawString(left_x, title_y, left_text)
c.drawCentredString(center_x, title_y, center_text)
c.drawRightString(right_x, title_y, right_text)

# Now set up a flow frame for the section heading + QA list taking remaining vertical space
frame_top = title_y - (0.4 * cm)
frame_bottom = FOOTER_BASELINE + 0.6 * cm  # keep a little space above footer
frame_height = frame_top - frame_bottom
frame = Frame(MARGIN, frame_bottom, usable_width, frame_height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)

styles = getSampleStyleSheet()
heading_style = ParagraphStyle('heading', parent=styles['Normal'], fontName=BOLD_FONT,
                               fontSize=HEADING_SIZE, leading=LINE_LEADING, alignment=TA_LEFT, spaceAfter=6)
qa_style = ParagraphStyle('qa', parent=styles['Normal'], fontName=TITLE_FONT,
                          fontSize=BODY_SIZE, leading=LINE_LEADING, alignment=TA_LEFT, leftIndent=0)

# Build story
story = []
story.append(Paragraph(section_heading, heading_style))
story.append(Spacer(1, 4))

for line in qa_lines:
    # Keep Q & A on one line by not allowing hyphenation; use non-breaking spaces for better control if required
    story.append(Paragraph(line, qa_style))

# Add story to frame (flows and wraps exactly within margins)
frame.addFromList(story, c)

# Draw footer baseline at exactly 1.25 cm from bottom
c.setFont(TITLE_FONT, 9)
c.drawCentredString(PAGE_WIDTH / 2, FOOTER_BASELINE, footer_text)

c.showPage()
c.save()
print("Saved:", pdf_out)
