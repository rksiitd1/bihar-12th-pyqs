"""
Reproduce page 1 exactly with:
- margins = 1.27 cm
- header image (1600x400 px aspect)
- page background = Blue Accent 5 Lighter 60% (approx)
- Q&A: Nirmala UI, size 8, leading 1.0 (i.e., leading = 8)
- number at 0.1 cm from left inside margin, text starts at 0.7 cm inside margin
- footer: Badoni MT, size 11, baseline at 1.25 cm from bottom
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# -----------------------
# Configuration / paths
# -----------------------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.27 * cm
FOOTER_BASELINE = 1.25 * cm

HEADER_IMAGE = "header.png"   # put header image here
NIRMALA_TTF = "Nirmala.ttf"   # optional: place Nirmala UI TTF in same folder
BADONI_TTF = "BadoniMT.ttf"   # optional: place Badoni MT TTF in same folder

OUTPUT = "page1_exact_design.pdf"

# Fonts names to register/use
NIRMALA_FONT_NAME = "NirmalaUI_Custom"
BADONI_FONT_NAME = "BadoniMT_Custom"

# -----------------------
# Visual metrics
# -----------------------
# header keeps 4:1 ratio (1600x400). header height computed to fill usable width inside margins.
usable_width = PAGE_WIDTH - 2 * MARGIN
HEADER_RATIO = 400.0 / 1600.0  # 0.25
header_height = usable_width * HEADER_RATIO
GAP_AFTER_HEADER = 0.25 * cm

# Q/A layout specifics
number_offset_inside_margin = 0.1 * cm   # from inside left margin
text_start_inside_margin = 0.7 * cm      # from inside left margin
font_size_qa = 8                          # Nirmala UI size 8
leading_qa = font_size_qa * 1.0           # line spacing 1.0 -> leading = 8

# footer font size
footer_font_size = 11

# Page background color: approximate "Blue, Accent 5, Lighter 60%"
# (approximate Hex chosen: #D6E6F8 -> (214,230,248))
PAGE_BG_RGB = (214/255.0, 230/255.0, 248/255.0)

# -----------------------
# Attempt to register fonts (try to use provided TTFs)
# -----------------------
def try_register_font(ttf_path, face_name):
    try:
        if os.path.isfile(ttf_path):
            pdfmetrics.registerFont(TTFont(face_name, ttf_path))
            print(f"Registered font {face_name} from {ttf_path}")
            return True
        else:
            # try common Windows system fonts folder (Windows only)
            win_path = os.path.join("C:\\", "Windows", "Fonts", ttf_path)
            if os.path.isfile(win_path):
                pdfmetrics.registerFont(TTFont(face_name, win_path))
                print(f"Registered font {face_name} from {win_path}")
                return True
    except Exception as e:
        print("Font registration error:", e)
    return False

nirmala_ok = try_register_font(NIRMALA_TTF, NIRMALA_FONT_NAME)
badoni_ok = try_register_font(BADONI_TTF, BADONI_FONT_NAME)

# Fallback mapping if custom not available
if not nirmala_ok:
    # try to register 'Nirmala UI' from system by file name (best-effort)
    # else fallback to Helvetica
    try:
        pdfmetrics.registerFont(TTFont(NIRMALA_FONT_NAME, "Nirmala.ttf"))
        nirmala_ok = True
    except:
        print("Nirmala UI TTF not found. Falling back to Helvetica for QA text.")
        NIRMALA_FONT_NAME = "Helvetica"

if not badoni_ok:
    try:
        pdfmetrics.registerFont(TTFont(BADONI_FONT_NAME, "BadoniMT.ttf"))
        badoni_ok = True
    except:
        print("Badoni MT TTF not found. Falling back to Times-Roman for footer.")
        BADONI_FONT_NAME = "Times-Roman"

# -----------------------
# Text content (page 1) - put full page lines here
# -----------------------
title_left = "Page 1 of 13"
title_center = "Shri Classes & DBG Gurukulam (by IITian Golu Sir)"
title_right = "https://dbggurukulam.com"
section_heading = "Quick revision: One-liner questions and answers"

# Q/A lines exactly as in page 1 (put full page 1 data here)
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

footer_text = "Shri Classes & DBG Gurukulam (by IITian Golu Sir) — https://dbggurukulam.com"

# -----------------------
# Helper: measure string width with chosen font
# -----------------------
def string_width(text, font_name, font_size):
    try:
        return pdfmetrics.stringWidth(text, font_name, font_size)
    except:
        # fallback measure with Helvetica if font not registered
        return pdfmetrics.stringWidth(text, "Helvetica", font_size)

# -----------------------
# Create PDF
# -----------------------
c = canvas.Canvas(OUTPUT, pagesize=A4)

# 1) Page background
c.setFillColorRGB(*PAGE_BG_RGB)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)

# 2) Draw header (image) inside margins, at top
header_x = MARGIN
header_y = PAGE_HEIGHT - MARGIN - header_height
if os.path.isfile(HEADER_IMAGE):
    c.drawImage(HEADER_IMAGE, header_x, header_y, width=usable_width, height=header_height, preserveAspectRatio=True)
else:
    # placeholder so layout can be checked without the image
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.rect(header_x, header_y, usable_width, header_height)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawCentredString(header_x + usable_width/2, header_y + header_height/2, "HEADER IMAGE MISSING - put header.png here")

# 3) Title line just under header
title_y = header_y - GAP_AFTER_HEADER - (0.1 * cm)
c.setFont("Times-Roman", 11)
# Left, center, right columns
c.drawString(MARGIN, title_y, title_left)
c.drawCentredString(PAGE_WIDTH / 2.0, title_y, title_center)
c.drawRightString(PAGE_WIDTH - MARGIN, title_y, title_right)

# 4) Section heading under title
heading_y = title_y - (0.4 * cm)
c.setFont("Times-Bold", 11)
c.drawString(MARGIN, heading_y, section_heading)

# 5) Q&A block - draw each line with manual wrapping
block_top = heading_y - (0.5 * cm)   # starting y for first QA line
current_y = block_top

number_x = MARGIN + number_offset_inside_margin
text_x = MARGIN + text_start_inside_margin
right_limit_x = PAGE_WIDTH - MARGIN
avail_width_for_text = right_limit_x - text_x

# Set QA font for drawing
qa_font = NIRMALA_FONT_NAME
c.setFillColorRGB(0, 0, 0)

for qa in qa_lines:
    # split into number and rest
    # expecting pattern like "1. Question - Answer"
    if '.' in qa:
        # first period after initial number
        parts = qa.split('.', 1)
        num_text = parts[0].strip() + '.'
        rest = parts[1].strip()
    else:
        num_text = ""
        rest = qa

    # Manual word-wrap using pdfmetrics.stringWidth
    words = rest.split()
    lines = []
    line = ""
    for w in words:
        candidate = line + (" " if line else "") + w
        if string_width(candidate, qa_font, font_size_qa) <= avail_width_for_text:
            line = candidate
        else:
            if line == "":
                # a single very long word (unlikely) - force it
                lines.append(candidate)
                line = ""
            else:
                lines.append(line)
                line = w
    if line:
        lines.append(line)

    # Check if there is space left on page for the required lines; if not, stop (we're reproducing page 1)
    needed_height = len(lines) * leading_qa
    bottom_limit = FOOTER_BASELINE + (0.3 * cm)
    if (current_y - needed_height) < bottom_limit:
        # Not enough space to render more QAs on this page (page break would be needed)
        break

    # draw number on the first line's baseline
    # baseline for first line is (current_y - (font_size_qa * 0.0)), but using drawString baseline as current_y - font_size_qa
    # we'll draw lines such that their y for drawString is current_y - font_size_qa (first line),
    # and subsequent lines at current_y - font_size_qa - n*leading_qa
    for i, ln in enumerate(lines):
        line_y = current_y - (i + 1) * leading_qa + (leading_qa - font_size_qa)
        # draw the text line
        try:
            c.setFont(qa_font, font_size_qa)
        except:
            c.setFont("Helvetica", font_size_qa)
        c.drawString(text_x, line_y, ln)

    # draw number at the first line baseline (align with first rendered line)
    first_line_y = current_y - 1 * leading_qa + (leading_qa - font_size_qa)
    try:
        c.setFont(qa_font, font_size_qa)
    except:
        c.setFont("Helvetica", font_size_qa)
    c.drawString(number_x, first_line_y, num_text)

    # move current_y down by used height
    current_y = current_y - needed_height - (0.1 * cm)  # add small gap between items

# 6) Footer (Badoni MT, size 11) exactly at baseline = 1.25 cm
try:
    c.setFont(BADONI_FONT_NAME, footer_font_size)
except:
    c.setFont("Times-Roman", footer_font_size)
c.setFillColorRGB(0, 0, 0)
c.drawCentredString(PAGE_WIDTH / 2.0, FOOTER_BASELINE, footer_text)

c.showPage()
c.save()

print("Saved PDF:", OUTPUT)
if not nirmala_ok:
    print("NOTE: Nirmala UI not available; used fallback font. To match exactly, place 'Nirmala.ttf' in script folder.")
if not badoni_ok:
    print("NOTE: Badoni MT not available; used fallback font. To match exactly, place 'BadoniMT.ttf' in script folder.")
