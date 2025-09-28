from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- PAGE SETTINGS ---
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm  # margins (top, bottom, left, right)
FOOTER_MARGIN = 1.25 * cm  # footer distance from bottom

# --- HEADER IMAGE (1600x400 px assumed as logo/banner) ---
HEADER_IMAGE = "header.png"   # replace with your actual image file

# --- TEXT CONTENT (from your first page) ---
content = """
Page 1 of 13   Shri Classes & DBG Gurukulam (by IITian Golu Sir)   https://dbggurukulam.com

Quick revision: One-liner questions and answers

1. What is the reproductive part of a flowering plant? - The flower.
2. What is the male part of a flower called? - The Androecium.
3. The androecium is made of what units? - Stamens.
4. A stamen has which two parts? - The anther and the filament.
5. What part of the anther makes pollen? - The microsporangium (or pollen sac).
6. What is the ploidy of a microspore mother cell? - Diploid (2n).
7. How do microspore mother cells form microspores? - Through meiosis.
8. What is the ploidy of a pollen grain? - Haploid (n).
9. What is the hard outer layer of pollen? - The exine.
10. What tough material makes the exine? - Sporopollenin.
11. What is the thin inner layer of pollen? - The intine.
12. Name the two cells in a mature pollen grain. - The vegetative cell and generative cell.
13. Which pollen cell is larger and forms the pollen tube? - The vegetative cell.
14. Which pollen cell forms the two male gametes? - The generative cell.
15. What is the female part of a flower called? - The Gynoecium (or pistil).
16. A pistil has which three parts? - Stigma, style, and ovary.
17. Which part of the pistil catches pollen? - The stigma.
18. What structure is found inside the ovary? - The ovule.
19. After fertilization, what does the ovule become? - The seed.
20. What sac inside the ovule holds the egg cell? - The embryo sac.
...
"""

# --- CREATE PDF ---
pdf_file = "output_page1.pdf"
c = canvas.Canvas(pdf_file, pagesize=A4)

# Draw header image
header_width = PAGE_WIDTH - 2 * MARGIN
c.drawImage(HEADER_IMAGE, MARGIN, PAGE_HEIGHT - MARGIN - 3*cm, 
            width=header_width, height=3*cm, preserveAspectRatio=True)

# Define text frame (below header, above footer)
frame = Frame(MARGIN, FOOTER_MARGIN + 1*cm, 
              PAGE_WIDTH - 2*MARGIN, PAGE_HEIGHT - (2*MARGIN + 3*cm))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_CENTER, fontSize=11, leading=14))

story = [Paragraph(line, styles['Normal']) for line in content.split("\n") if line.strip()]

frame.addFromList(story, c)

# Footer
c.setFont("Helvetica", 9)
c.drawCentredString(PAGE_WIDTH / 2, FOOTER_MARGIN / 2, "Confidential - Shri Classes & DBG Gurukulam")

c.save()
print("PDF created:", pdf_file)
