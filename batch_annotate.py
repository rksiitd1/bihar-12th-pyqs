import pathlib
import time
import json
from annotate_questions_with_chapters import CHAPTERS, clean_json_response
import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Gemini API key not found. Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=GOOGLE_API_KEY)

def generate_annotation_prompt(subject, chapters, questions):
    chapter_lines = [f"{i+1}. {ch}" for i, ch in enumerate(chapters)]
    prompt = f"""
You are an expert in educational content classification.
You will receive a JSON array of questions from a Class 12 {subject.title()} question paper.
Your task is to annotate each question with the correct chapter number (as a string, e.g., \"1\", \"2\", etc.) from the official NCERT Class 12 {subject.title()} chapters below.
- Insert the field \"chapter\": \"<number>\" immediately after the \"type\" field in each question object.
- Only use the chapter numbers from the list below.
- Output the result as a JSON array, with the \"chapter\" field added to each question.

Here are the chapters:
{chr(10).join(chapter_lines)}

Here is the input JSON array of questions:
```json
{json.dumps(questions, ensure_ascii=False, indent=2)}
```

Output only the annotated JSON array.
"""
    return prompt

def annotate_file(subject, input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    chapters = CHAPTERS[subject]
    prompt = generate_annotation_prompt(subject, chapters, questions)
    model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
    response = model.generate_content(prompt)
    try:
        cleaned_json_string = clean_json_response(response.text)
        annotated = json.loads(cleaned_json_string)
    except Exception as e:
        print(f"\n--- ERROR: Failed to parse Gemini's response for {input_path.name}. ---")
        print(f"Error details: {e}")
        print("\n--- Raw Model Response: ---")
        print(response.text)
        print("\n--------------------------")
        return False
    # Add chapter_name to each question
    for q in annotated:
        chapter_num = q.get("chapter")
        if chapter_num is not None and "chapter_name" not in q:
            try:
                idx = int(chapter_num) - 1
                if 0 <= idx < len(chapters):
                    q["chapter_name"] = chapters[idx]
            except Exception:
                pass
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(annotated, f, indent=4, ensure_ascii=False)
    return True

def main():
    subjects = list(CHAPTERS.keys())
    print("Available subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s.title()}")
    while True:
        choice = input(f"Select subject (1-{len(subjects)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(subjects):
            subject = subjects[int(choice)-1]
            break
        print("Please enter a valid number.")

    data_folder = pathlib.Path(f"{subject}_data")
    annotated_folder = pathlib.Path(f"{subject}_data_annotated")
    annotated_folder.mkdir(exist_ok=True)
    if not data_folder.exists():
        print(f"{data_folder} does not exist!")
        return
    json_files = list(data_folder.glob("*.json"))
    print(f"\nSubject: {subject.title()} | {len(json_files)} files found.")
    for json_file in json_files:
        annotated_file = annotated_folder / json_file.name
        if annotated_file.exists():
            print(f"⏭️  Skipping {json_file.name} (already annotated)")
            continue
        print(f"Annotating {json_file.name} ...", end=" ")
        start = time.time()
        success = annotate_file(subject, json_file, annotated_file)
        end = time.time()
        if success:
            print(f"✓ Done in {end-start:.1f}s")
        else:
            print(f"❌ Failed")

if __name__ == "__main__":
    main()
