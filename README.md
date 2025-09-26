# PYQS (Previous Year Question Papers) Processing System

This project contains a collection of Python scripts for processing, annotating, and extracting data from Class 12 question papers (Biology, Chemistry, Physics, and Mathematics) from Bihar Board.

## Script Overview

### 1. **pyqs.py**
Downloads question paper PDFs from Bihar Board's official website for specified subjects and years (2009-2025).

### 2. **process_paper.py**
Main processing script that extracts questions from PDF files using Google's Gemini AI. Converts PDFs to structured JSON format with bilingual support (English/Hindi) and proper LaTeX formatting for mathematical expressions.

### 3. **batch_processing.py**
Batch processes multiple physics question papers automatically, skipping already processed files to avoid duplicate work.

### 4. **annotate_questions_with_chapters.py**
Interactive script that uses Gemini AI to annotate questions with their corresponding chapter numbers and names based on NCERT Class 12 curriculum.

### 5. **annotate_questions_with_topics_physics.py**
Specialized script for physics questions that annotates both chapter and topic information with detailed topic breakdowns for each chapter.

### 6. **batch_annotate.py**
Batch processes all JSON files for a selected subject, adding chapter annotations using Gemini AI. Includes progress tracking and error handling.

### 7. **batch_annotate_physics.py**
Batch processes all physics JSON files with both chapter and topic annotations, similar to the individual physics annotator but for multiple files.

### 8. **add_chapter_names_to_annotated.py**
Utility script that adds chapter names to already annotated files that only have chapter numbers, using the predefined chapter lists.

### 9. **reorder_chapter_name.py**
Reorders JSON fields to place `chapter_name` immediately after `chapter` field for better data organization.

### 10. **reorder_chapter_name_all.py**
Batch version of the reordering script that processes all JSON files in a specified folder.

### 11. **extract_long_questions.py**
Extracts all long answer questions from chemistry data files and consolidates them into a single JSON file with year-wise organization.

### 12. **extract_short_questions.py**
Extracts all short answer questions from chemistry data files and consolidates them into a single JSON file with year-wise organization.

### 13. **extract_objective_questions.py**
Extracts all objective (multiple choice) questions from chemistry data files and consolidates them into a single JSON file with year-wise organization.

### 14. **json_to_excel_converter.py**
Converts JSON question data to Excel format with proper column formatting, auto-adjusting column widths, and bilingual support.

## Data Structure

The processed questions follow this JSON structure:
```json
{
  "id": "obj_1",
  "type": "objective|short_answer|long_answer",
  "chapter": "1",
  "chapter_name": "Chapter Name",
  "topic": "1.1",
  "topic_name": "Topic Name",
  "question": "English question text",
  "prashna": "Hindi question text",
  "options": {"A": "Option A", "B": "Option B", ...},
  "vikalpa": {"A": "विकल्प A", "B": "विकल्प B", ...},
  "answer": "Correct answer",
  "uttar": "सही उत्तर"
}
```

## Folder Structure

- `{subject}_papers/` - Contains downloaded PDF files
- `{subject}_data/` - Contains processed JSON files
- `{subject}_data_annotated/` - Contains annotated JSON files with chapter/topic information
- `extracts/` - Contains consolidated question extractions by type

## Prerequisites

- Python 3.x
- Google Gemini API key (set as `GOOGLE_API_KEY` environment variable)
- Required packages: `google-generativeai`, `pandas`, `xlsxwriter`, `requests`

## Usage Workflow

1. **Download papers**: Run `pyqs.py` to download question papers
2. **Process PDFs**: Use `process_paper.py` or `batch_processing.py` to convert PDFs to JSON
3. **Annotate questions**: Use annotation scripts to add chapter/topic information
4. **Extract specific types**: Use extraction scripts to get questions by type
5. **Convert to Excel**: Use `json_to_excel_converter.py` for spreadsheet format

## Features

- Bilingual support (English/Hindi)
- LaTeX formatting for mathematical expressions
- Batch processing capabilities
- Error handling and progress tracking
- Multiple output formats (JSON, Excel)
- Organized data structure with proper field ordering
