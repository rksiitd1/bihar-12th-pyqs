import os
import google.generativeai as genai
import json
import pathlib
import textwrap
import re
from dotenv import load_dotenv

def clean_json_response(raw_text: str) -> str:
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

GEOGRAPHY_CHAPTERS = [
    # Part A: Fundamentals of Human Geography
    "Human Geography Nature and Scope",
    "The World Population Distribution, Density and Growth",
    "Population Composition",
    "Human Development",
    "Primary Activities",
    "Secondary Activities",
    "Tertiary and Quaternary Activities",
    "Transport and Communication",
    "International Trade",
    "Human Settlements",
    
    # Part B: India: People and Economy
    "Population: Distribution, Density, Growth and Composition",
    "Migration: Types, Causes and Consequences",
    "Human Development (India)",
    "Human Settlements (India)",
    "Land Resources and Agriculture",
    "Water Resources",
    "Mineral and Energy Resources",
    "Manufacturing Industries",
    "Planning and Sustainable Development in Indian Context",
    "Transport and Communication (India)",
    "International Trade (India)",
    "Geographical Perspective on Selected Issues and Problems"
]

def generate_geography_annotation_prompt(chapters, questions):
    chapter_lines = [f"{ch}" for ch in chapters]
    prompt = textwrap.dedent(f"""
    You are an expert in educational content classification.
    You will receive a JSON array of questions from a Class 12 Geography question paper.
    Your task is to annotate each question with the correct chapter name from the official NCERT Class 12 Geography chapters below.
    - Insert the fields "chapter_name": "<name>" immediately after the "type" field in each question object.
    - Only use the exact chapter names from the list below.
    - Output the result as a JSON array, with the new fields added to each question.

    Chapters:
    {chr(10).join(chapter_lines)}

    Here is the input JSON array of questions:
    ```json
    {json.dumps(questions, ensure_ascii=False, indent=2)}
    ```

    Output only the annotated JSON array.
    """)
    return prompt

def main():
    print("Batch Geography Question Annotator (Gemini)")
    print("="*40)
    data_folder = pathlib.Path("geography_data")
    out_folder = pathlib.Path("geography_data_annotated")
    out_folder.mkdir(exist_ok=True)
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in geography_data/!")
        return
    chapters = GEOGRAPHY_CHAPTERS
    model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")
    for fpath in files:
        out_path = out_folder / fpath.name
        if out_path.exists():
            print(f"⏭️  Skipping {fpath.name} (already annotated)")
            continue
            
        print(f"\nProcessing: {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        prompt = generate_geography_annotation_prompt(chapters, questions)
        print("Sending questions to Gemini for annotation...")
        response = model.generate_content(prompt)
        print("Gemini response received. Parsing...")
        try:
            cleaned_json_string = clean_json_response(response.text)
            annotated = json.loads(cleaned_json_string)
        except Exception as e:
            print(f"\n--- ERROR: Failed to parse Gemini's response for {fpath.name}. ---")
            print(f"Error details: {e}")
            print("\n--- Raw Model Response: ---")
            print(response.text)
            print("\n--------------------------")
            continue
        # Reorder fields
        for i, q in enumerate(annotated):
            if "type" in q and "chapter_name" in q:
                new_q = {}
                for k, v in q.items():
                    new_q[k] = v
                    if k == "type":
                        # Also add a dummy chapter number for consistency if needed, 
                        # but for now we rely on chapter_name
                        new_q["chapter_name"] = q["chapter_name"]
                annotated[i] = new_q
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(annotated, f, indent=4, ensure_ascii=False)
        print(f"✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    load_dotenv()
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("Gemini API key not found. Please set the GOOGLE_API_KEY environment variable.")
    genai.configure(api_key=GOOGLE_API_KEY)
    main()
