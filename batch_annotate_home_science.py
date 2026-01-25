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

HOME_SCIENCE_CHAPTERS = [
    "Work, Livelihood and Career",
    "Clinical Nutrition and Dietetics",
    "Public Nutrition and Health",
    "Food Processing and Technology",
    "Food Quality and Food Safety",
    "Early Childhood Care and Education",
    "Guidance and Counselling",
    "Special Education and Support Services",
    "Management of Support Services, Institutions and Programmes for Children, Youth and Elderly",
    "Design for Fabric and Apparel",
    "Fashion Design and Merchandising",
    "Production and Quality Control in the Garment Industry",
    "Textile Conservation in Museums",
    "Care and Maintenance of Fabrics in Institutions",
    "Human Resource Management",
    "Hospitality Management",
    "Ergonomics and Designing of Interior and Exterior Spaces",
    "Event Management",
    "Consumer Education and Protection",
    "Development Communication and Journalism",
    "Advocacy",
    "Media Management, Design, and Production",
    "Corporate Communication and Public Relations",
    "Management of Development Programme"
]

def generate_home_science_annotation_prompt(chapters, questions):
    chapter_lines = [f"{ch}" for ch in chapters]
    prompt = textwrap.dedent(f"""
    You are an expert in educational content classification.
    You will receive a JSON array of questions from a Class 12 Home Science question paper.
    Your task is to annotate each question with the correct chapter name from the official NCERT Class 12 Home Science chapters below.
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
    print("Batch Home Science Question Annotator (Gemini)")
    print("="*40)
    data_folder = pathlib.Path("home_science_data")
    out_folder = pathlib.Path("home_science_data_annotated")
    out_folder.mkdir(exist_ok=True)
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in home_science_data/!")
        return
    chapters = HOME_SCIENCE_CHAPTERS
    model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
    for fpath in files:
        out_path = out_folder / fpath.name
        if out_path.exists():
            print(f"⏭️  Skipping {fpath.name} (already annotated)")
            continue
            
        print(f"\nProcessing: {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        prompt = generate_home_science_annotation_prompt(chapters, questions)
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
