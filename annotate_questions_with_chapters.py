import os
import google.generativeai as genai
import json
import pathlib
import textwrap
import re
import time
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Gemini API key not found. Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=GOOGLE_API_KEY)

# --- Chapter Lists ---
CHAPTERS = {
    "biology": [
        "Sexual Reproduction in Flowering Plants",
        "Human Reproduction",
        "Reproductive Health",
        "Principles of Inheritance and Variation",
        "Molecular Basis of Inheritance",
        "Evolution",
        "Human Health and Disease",
        "Microbes in Human Welfare",
        "Biotechnology: Principles and Processes",
        "Biotechnology and its Applications",
        "Organisms and Populations",
        "Ecosystem",
        "Biodiversity and Conservation"
    ],
    "chemistry": [
        "The Solid State",
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "Surface Chemistry",
        "General Principles and Processes of Isolation of Elements",
        "The p-Block Elements",
        "The d- and f-Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Amines",
        "Biomolecules",
        "Polymers",
        "Chemistry in Everyday Life"
    ],
    "physics": [
        "Electric Charges and Fields",
        "Electrostatic Potential and Capacitance",
        "Current Electricity",
        "Moving Charges and Magnetism",
        "Magnetism and Matter",
        "Electromagnetic Induction",
        "Alternating Current",
        "Electromagnetic Waves",
        "Ray Optics and Optical Instruments",
        "Wave Optics",
        "Dual Nature of Radiation and Matter",
        "Atoms",
        "Nuclei",
        "Semiconductor Electronics: Materials, Devices and Simple Circuits",
        "Communication Systems"
    ],
    "mathematics": [
        "Relations and Functions",
        "Inverse Trigonometric Functions",
        "Matrices",
        "Determinants",
        "Continuity and Differentiability",
        "Application of Derivatives",
        "Integrals",
        "Application of Integrals",
        "Differential Equations",
        "Vector Algebra",
        "Three Dimensional Geometry",
        "Linear Programming",
        "Probability"
    ]
}

# --- Utility Functions ---
def clean_json_response(raw_text: str) -> str:
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def get_subject():
    subjects = list(CHAPTERS.keys())
    print("\nAvailable subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s.title()}")
    while True:
        choice = input(f"Select subject (1-{len(subjects)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(subjects):
            return subjects[int(choice)-1]
        print("Please enter a valid number.")

def get_json_files(subject):
    data_folder = pathlib.Path(f"{subject}_data")
    if not data_folder.exists():
        print(f"{data_folder}/ folder not found!")
        return []
    return list(data_folder.glob("*.json"))

def select_file(files):
    print("\nAvailable JSON files:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f.name}")
    while True:
        choice = input(f"Select file number (1-{len(files)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice)-1]
        print("Please enter a valid number.")

def generate_annotation_prompt(subject, chapters, questions):
    chapter_lines = [f"{i+1}. {ch}" for i, ch in enumerate(chapters)]
    prompt = textwrap.dedent(f"""
    You are an expert in educational content classification.
    You will receive a JSON array of questions from a Class 12 {subject.title()} question paper.
    Your task is to annotate each question with the correct chapter number (as a string, e.g., "1", "2", etc.) from the official NCERT Class 12 {subject.title()} chapters below.
    - Insert the field "chapter": "<number>" immediately after the "type" field in each question object.
    - Only use the chapter numbers from the list below.
    - Output the result as a JSON array, with the "chapter" field added to each question.

    Here are the chapters:
    {chr(10).join(chapter_lines)}

    Here is the input JSON array of questions:
    ```json
    {json.dumps(questions, ensure_ascii=False, indent=2)}
    ```

    Output only the annotated JSON array.
    """)
    return prompt

def main():
    print("Question Chapter Annotator (Gemini)")
    print("="*40)
    subject = get_subject()
    files = get_json_files(subject)
    if not files:
        print(f"No JSON files found in {subject}_data/!")
        return
    selected_file = select_file(files)
    print(f"\nLoading: {selected_file.name}")
    with open(selected_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    chapters = CHAPTERS[subject]
    prompt = generate_annotation_prompt(subject, chapters, questions)
    print("\nSending questions to Gemini for chapter annotation...")
    model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")
    response = model.generate_content(prompt)
    print("Gemini response received. Parsing...")
    try:
        cleaned_json_string = clean_json_response(response.text)
        annotated = json.loads(cleaned_json_string)
    except Exception as e:
        print(f"\n--- ERROR: Failed to parse Gemini's response. ---")
        print(f"Error details: {e}")
        print("\n--- Raw Model Response: ---")
        print(response.text)
        print("\n--------------------------")
        return

    # Add chapter_name immediately after chapter field in each question
    for i, q in enumerate(annotated):
        chapter_num = q.get("chapter")
        if chapter_num is not None:
            try:
                idx = int(chapter_num) - 1
                if 0 <= idx < len(chapters):
                    chapter_name = chapters[idx]
                    # Insert chapter_name just after chapter
                    new_q = {}
                    for k, v in q.items():
                        new_q[k] = v
                        if k == "chapter":
                            new_q["chapter_name"] = chapter_name
                    annotated[i] = new_q
            except Exception:
                pass

    out_folder = pathlib.Path(f"{subject}_data_annotated")
    out_folder.mkdir(exist_ok=True)
    out_path = out_folder / selected_file.name
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(annotated, f, indent=4, ensure_ascii=False)
    print(f"\n✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    main() 
