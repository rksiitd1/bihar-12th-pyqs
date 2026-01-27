
import os
import json
import base64
import time
from google import genai
from google.genai import types

# --- Configuration ---
# You can adjust model names here
MODEL_PRO = "gemini-1.5-pro" # or "gemini-3-pro-preview" as per user snippet
MODEL_FLASH = "gemini-1.5-flash"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input():
    """Gets necessary inputs from the user."""
    print("--- Exam Question Predictor ---")
    
    # 1. Select Subject / Folder
    # Assuming folders are in the current working directory, 
    # and we look for folders ending with '_data_annotated' or similar, 
    # OR just list subdirectories.
    # The prompt says "input can be asked to be selected using ticker".
    # We'll list directories and ask user to pick.
    
    current_dir = os.getcwd()
    subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(d) and not d.startswith('.')]
    
    # Filter for likely candidates if needed, or just show all
    # For now, let's show all and let user pick.
    print("\nAvailable Folders:")
    for i, d in enumerate(subdirs):
        print(f"{i + 1}. {d}")
    
    while True:
        try:
            choice = int(input("\nSelect folder number: "))
            if 1 <= choice <= len(subdirs):
                selected_folder = subdirs[choice - 1]
                break
            print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

    folder_path = os.path.join(current_dir, selected_folder)
    
    # 2. Subject Name
    # Try to decipher from folder name, or ask.
    subject_default = selected_folder.replace('_data', '').replace('_', ' ').title()
    subject_name = input(f"Subject Name [{subject_default}]: ").strip() or subject_default

    # 3. Parameters
    try:
        total_questions = int(input("Total LONG questions asked in exam (e.g., 8): ") or "8")
        to_solve = int(input("Questions to be solved (e.g., 4): ") or "4")
    except ValueError:
        print("Using defaults: 8 asked, 4 to solve.")
        total_questions = 8
        to_solve = 4

    return folder_path, subject_name, total_questions, to_solve

def find_json_file(folder_path):
    """Finds the merged json file in the folder."""
    # Heuristic: look for 'merged_*.json' or just any .json that looks big
    # User said "where to save... would be same as the input folder".
    for f in os.listdir(folder_path):
        if f.endswith('.json') and 'merged' in f:
             return os.path.join(folder_path, f)
    
    # Fallback: list jsons
    jsons = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    if not jsons:
        return None
    
    if len(jsons) == 1:
        return os.path.join(folder_path, jsons[0])
    
    print("\nJSON files found:")
    for i, f in enumerate(jsons):
        print(f"{i + 1}. {f}")
    
    while True:
        try:
            choice = int(input("Select JSON file: "))
            if 1 <= choice <= len(jsons):
                return os.path.join(folder_path, jsons[choice-1])
        except:
            pass
    return None

def analyze_and_generate_12(client, json_content, subject_name, total_questions, to_solve, years_count):
    """Step 1: Analyze JSON and generate 12 important questions."""
    print("\n--> Step 1: Analyzing data and selecting 12 questions (using Pro model)...")
    
    prompt_text = f"""These are Class 12 Bihar Board {subject_name} long-answer questions collected from the past {years_count} years of board examinations. Only long-answer type questions are included.

The dataset contains the questions. In the actual examination, {total_questions} long-answer questions are asked, and students are required to attempt only {to_solve}.

Your task is to analyze all questions and identify the 12 most important questions that students must study to maximize their chances of success.

You must follow the logical methodology below strictly and systematically:

Frequency Analysis
Count how many times each question, or its close variants, has appeared.
Assign a frequency score to each question.

Conceptual Clustering
Group questions that test the same core concept, even if their wording is different.
Treat rephrased or slightly modified questions as conceptually identical.

Trend Detection Over Time
Identify questions or concepts that:
Appear repeatedly in recent years, or
Reappear at regular intervals (for example, every 2–3 years).

Syllabus Centrality Weighting
Give higher importance to questions derived from:
Core chapters
Foundational concepts
Topics that connect multiple chapters
Reduce weight for highly niche or isolated questions.

Exam-Setter Behavior Modeling
Assume the examiner prefers:
Conceptually rich questions
Questions that allow step-by-step explanation
Questions that test both understanding and presentation
Penalize questions that are too narrow or purely factual.

Coverage Optimization Constraint
The final set of 12 questions must:
Cover maximum syllabus breadth
Minimize overlap of underlying concepts
Ensure that at least {to_solve} questions from the set are likely to appear together in the exam.

Probability-Based Selection
Assign an estimated probability of appearance to each shortlisted question.
Select the final 12 questions such that the combined probability of being able to answer any {to_solve} out of {total_questions} exam questions is maximized.

Output Requirements:
Present the final 12 questions in a numbered list.
For each question, briefly mention:
Why it was selected (frequency, trend, core concept, etc.)
The main concept it tests.
Avoid vague statements; base all decisions strictly on the above logical steps.

Objective:
The goal is to ensure that a student who thoroughly prepares only these 12 questions will be able to confidently attempt all four required long-answer questions and achieve excellent marks in the examination."""

    # Using base64 to match user snippet style, but text passing is also fine.
    # User's snippet used base64, so we stick to it for the data part.
    json_bytes = json_content.encode('utf-8')
    encoded_json = base64.b64encode(json_bytes).decode('utf-8')
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="application/json",
                    data=base64.b64decode(encoded_json) 
                ),
                types.Part.from_text(text=prompt_text)
            ]
        )
    ]
    
    response = client.models.generate_content(
        model=MODEL_PRO,
        contents=contents
    )
    return response.text, contents + [types.Content(role="model", parts=[types.Part.from_text(text=response.text)])]

def extend_to_20(client, history):
    """Step 2: Extend to 20 questions."""
    print("\n--> Step 2: Extending list to 20 questions (using Pro model)...")
    
    prompt_text = "please provide 20, in the order which has highest probable question on top"
    
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))
    
    response = client.models.generate_content(
        model=MODEL_PRO,
        contents=history
    )
    return response.text, history + [types.Content(role="model", parts=[types.Part.from_text(text=response.text)])]

def extract_questions_text(client, history):
    """Step 3: Extract just the question text."""
    print("\n--> Step 3: Extracting question text (using Flash model)...")
    
    prompt_text = "Please write down the questions, just the questions..."
    
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))
    
    response = client.models.generate_content(
        model=MODEL_FLASH, # Switching to Flash as requested for subsequent prompts
        contents=history
    )
    return response.text, history + [types.Content(role="model", parts=[types.Part.from_text(text=response.text)])]

def translate_to_hindi(client, history):
    """Step 4: Translate to Hindi."""
    print("\n--> Step 4: Translating to Hindi (using Flash model)...")
    
    prompt_text = "in Hindi please"
    
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))
    
    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=history
    )
    return response.text, history + [types.Content(role="model", parts=[types.Part.from_text(text=response.text)])]

def generate_answers(client, history, subject_name):
    """Step 5: Generate detailed answers."""
    print("\n--> Step 5: Generating detailed answers (using Flash model)...")
    
    prompt_text = f"""You are an expert teacher for Bihar Board Class 12 [{subject_name}]. 

I am providing you with 20 important Long Answer Questions. Your task is to write detailed, exam-perfect answers for them in Hindi.

**Strict Guidelines for Answers:**
1. **Length:** Each answer must be 120–150 words (suitable for 5 marks).
2. **Structure:** Do not write huge paragraphs. Use points, bullet lists, sub-headings (A, B, C), and numbered steps.
3. **Detail:** Include definitions, principles, formulas, chemical reactions, or diagrams (described in text) wherever necessary.
4. **Tone:** Academic, clear, and easy to memorize for a student."""
    
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))
    
    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=history
    )
    return response.text, history + [types.Content(role="model", parts=[types.Part.from_text(text=response.text)])]

def generate_html(client, history, subject_name):
    """Step 6: Generate HTML."""
    print("\n--> Step 6: Formatting as HTML (using Flash model)...")
    
    prompt_text = f"""Now, convert the Question & Answer content you just generated into a print-ready HTML document. 

You must use the EXACT CSS and HTML structure provided below. Do not change the font sizes, margins, or class names.

**HTML & CSS TEMPLATE TO USE:**

<!DOCTYPE html>
<html lang=\"hi\">
<head>
    <meta charset=\"UTF-8\">
    <title>Class 12 Important Questions</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@400;600;700&family=Noto+Serif:wght@400;700&display=swap');
        @media print {{
            @page {{ size: A4 portrait; margin: 10mm; }}
            body {{ -webkit-print-color-adjust: exact; margin: 0; padding: 0; }}
        }}
        body {{
            font-family: 'Noto Serif Devanagari', 'Noto Serif', serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #000;
            background: #fff;
            text-align: justify;
        }}
        .content-wrapper {{
            column-count: 2;
            column-gap: 6mm;
            column-rule: 0.5px solid #ccc;
            width: 100%;
        }}
        h1 {{
            font-size: 16pt;
            font-weight: 700;
            text-align: center;
            text-transform: uppercase;
            margin: 0 0 5px 0;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
            column-span: all;
        }}
        .subtitle {{
            text-align: center; font-size: 9pt; font-style: italic; margin-bottom: 10px; column-span: all; color: #444;
        }}
        .qa-container {{
            break-inside: avoid; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dotted #999;
        }}
        .question {{
            font-weight: 700; font-size: 10.5pt; display: block; margin-bottom: 4px; background-color: #f0f0f0; padding: 3px 5px; border-left: 4px solid #000;
        }}
        .answer {{ display: block; margin-left: 2px; }}
        strong {{ font-weight: 700; }}
        p {{ margin: 2px 0; }}
        ul, ol {{ margin: 3px 0 5px 16px; padding: 0; }}
        li {{ margin-bottom: 2px; padding-left: 2px; }}
        .equation-box {{
            display: flex; justify-content: center; align-items: center; margin: 5px 0; padding: 4px; background: #fff; border: 1px solid #ddd; font-family: 'Times New Roman', serif; font-size: 9.5pt; font-style: italic; font-weight: 600; text-align: center;
        }}
        table {{
            width: 100%; border-collapse: collapse; font-size: 9pt; margin: 4px 0;
        }}
        th, td {{ border: 1px solid #000; padding: 2px 4px; vertical-align: top; }}
        th {{ background-color: #eee; text-align: center; font-weight: 700; }}
    </style>
</head>
<body>
    <h1>{subject_name} - Long Answer Questions</h1>
    <div class=\"subtitle\">Class 12 Bihar Board | Detailed 5-Marks Solutions | Top 20 Questions</div>
    <div class=\"content-wrapper\">
        <!-- INSERT CONTENT HERE -->
    </div>
</body>
</html>

**Formatting Rules:**
1. Wrap every Question-Answer pair inside `<div class=\"qa-container\">`.
2. Put the question text inside `<div class=\"question\">`.
3. Put the answer text inside `<div class=\"answer\">`.
4. If there is a formula, chemical reaction, or math expression, wrap it in `<div class=\"equation-box\">`.
5. Use `<table>` for differences/comparisons.
6. Use `<strong>` for headings inside the answer.
7. Output only the full HTML code."""

    history.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))
    
    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=history
    )
    return response.text, history

def save_html(html_content, folder_path, subject_name):
    """Saves the extracted HTML content to a file."""
    # Strip markdown code blocks if present
    clean_html = html_content.strip()
    if clean_html.startswith("```html"):
        clean_html = clean_html.replace("```html", "", 1)
    if clean_html.endswith("```"):
        clean_html = clean_html[:-3]
    
    clean_html = clean_html.strip()
    
    filename = f"{subject_name.lower().replace(' ', '_')}_important_questions.html"
    filepath = os.path.join(folder_path, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean_html)
    
    print(f"\n[SUCCESS] File saved at: {filepath}")

def main():
    clear_screen()
    
    # 1. Setup
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    client = genai.Client(api_key=api_key)

    # 2. User Input
    target_folder, subject_name, total_q, solve_q = get_user_input()
    
    print(f"\nProcessing folder: {target_folder}")
    print(f"Subject: {subject_name}")
    
    # 3. Read JSON
    json_path = find_json_file(target_folder)
    if not json_path:
        print("Error: No merged JSON file found in the selected folder.")
        return

    print(f"Reading data from: {os.path.basename(json_path)}")
    with open(json_path, "r", encoding="utf-8") as f:
        json_content = f.read()
    
    # Count years roughly
    try:
        data = json.loads(json_content)
        years_count = len(data.keys())
    except:
        years_count = 5 # default
    
    print(f"Detected {years_count} years of data.")
    
    # 4. Prompt Chaining
    try:
        # Step 1
        res1, history = analyze_and_generate_12(client, json_content, subject_name, total_q, solve_q, years_count)
        
        # Step 2
        res2, history = extend_to_20(client, history)
        
        # Step 3
        res3, history = extract_questions_text(client, history)
        
        # Step 4
        res4, history = translate_to_hindi(client, history)
        
        # Step 5
        res5, history = generate_answers(client, history, subject_name)
        
        # Step 6
        html_out, history = generate_html(client, history, subject_name)
        
        # 5. Save
        save_html(html_out, target_folder, subject_name)
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
