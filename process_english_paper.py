import os
import google.generativeai as genai
import json
import argparse
import pathlib
import textwrap
import re
import time
from dotenv import load_dotenv

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# Set your API key securely.
# It's recommended to use environment variables or a secrets manager.
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("Gemini API key not found. Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=GOOGLE_API_KEY)


# --- Core Functions ---

def clean_json_response(raw_text: str) -> str:
    """
    Cleans the raw text response from the Gemini API to extract a valid JSON string.
    It removes markdown code fences and any leading/trailing text.
    """
    # Use regex to find the JSON block within markdown fences
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback for responses that might not have the fences but are still valid JSON
    return raw_text.strip()


def generate_extraction_prompt(uploaded_file_uri: str) -> list:
    """
    Constructs the detailed prompt for the Gemini API, including the file
    and the specific instructions for JSON extraction and formatting.
    """
    prompt = textwrap.dedent("""
    Your task is to act as an expert data extraction engine. You will receive a PDF file of a Bihar Board Class 12 English question paper. You must meticulously extract all questions and convert them into a single, clean JSON array.

    Follow these instructions precisely:

    1.  **JSON Structure**: The output must be a JSON array where each element is an object representing a single question.
    2.  **Required Fields for All Questions**:
        - `id`: A unique string identifier. For each question type, numbering must start from 1. 
          - Examples: "obj_1", "essay_1", "exp_1", "letter_1", "short_1", "long_1", "passage_1", "precis_1".
          - The numbering for each type must always start at 1.
        - `type`: The question type. You MUST categorize each question into one of the following granular types:
          - `objective`: Section A (Grammar + Literature MCQs).
          - `essay`: Nibandh/Composition.
          - `explanation`: Reference to context (Prose/Poetry).
          - `letter_application`: Formal/Informal letter or application.
          - `short_answer`: 2-mark literature questions or similar.
          - `long_answer`: 5-mark literature or summary questions.
          - `passage_comprehension`: Questions based on unseen passages.
          - `precis`: Sankshepan/Summary.
        - `question`: The full English text of the question.
        - `prashna`: The full Hindi text of the question (if available). If not available, leave it as an empty string "" or null, OR if specifically instructed to translate, translate it. **Policy for English paper**: Since this is an English paper, instructions are usually in English. If a question is purely in English and has no Hindi equivalent in the paper, set `prashna` to the same as `question` or a reasonable translation if you can, but primarily `question` is key. **Actually, for consistency with other pipelines, if Hindi is missing, please translate the English question to Hindi for the `prashna` field.**

    3.  **Handling Alternatives**:
        - If two or more questions are given as alternatives (using "or"/"athva"), represent them as distinct objects with IDs like `long_1_1`, `long_1_2`.

    4.  **Fields for "objective" Type Questions**:
        - `options`: An object containing the English options, with keys "A", "B", "C", "D".
        - `vikalpa`: An object containing the Hindi options (translate if missing), with keys "A", "B", "C", "D".

    5.  **Fields for Questions with Sub-Questions**:
        - If a question contains sub-questions (e.g., in passage comprehension), include:
            - `sub_questions`: An object containing the sub-questions, with keys like "A", "B" or "1", "2".
            - `anuprashna`: Translated Hindi version.

    6.  **Accuracy & Formatting**:
        - Extract text exactly as it appears.
        - Preserve formatting where possible.
        - Do not add external text.

    The PDF file is provided. Begin processing now and generate only the JSON array as your output.
    """)

    return [
        {'text': prompt},
        {'file_data': {
            'mime_type': 'application/pdf',
            'file_uri': uploaded_file_uri
        }}
    ]

def process_question_paper(input_pdf_path: str, output_json_path: str):
    """
    Main function to process a question paper PDF and generate a structured JSON file.
    """
    start_time = time.time()
    print(f"Starting processing for: {input_pdf_path}")
    input_path = pathlib.Path(input_pdf_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found at: {input_pdf_path}")

    # Step 1: Upload the file to the Gemini File API
    print("Uploading file to the File API...")
    uploaded_file = genai.upload_file(path=input_path, display_name=input_path.name)
    print(f"File uploaded successfully: {uploaded_file.uri}")

    # Step 2: Construct the detailed prompt
    prompt_parts = generate_extraction_prompt(uploaded_file.uri)

    # Step 3: Call the Gemini API to generate the content
    print("Generating content with Gemini... (This may take a moment)")
    model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
    # model = genai.GenerativeModel(model_name="models/gemini-1.5-pro") # Fallback if needed
    response = model.generate_content(prompt_parts)

    # Step 4: Clean and parse the response
    print("Cleaning and parsing the JSON response...")
    try:
        cleaned_json_string = clean_json_response(response.text)
        data = json.loads(cleaned_json_string)
    except json.JSONDecodeError as e:
        print("\n--- ERROR: Failed to decode JSON from the model's response. ---")
        print(f"Error details: {e}")
        print("\n--- Raw Model Response: ---")
        print(response.text)
        print("\n--------------------------")
        return # Exit without writing a file
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("\n--- Raw Model Response: ---")
        print(response.text)
        return

    # Step 5: Write the structured data to the output file
    output_path = pathlib.Path(output_json_path)
    print(f"Writing structured data to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False is crucial for correctly writing Hindi characters
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("\nProcessing complete! The JSON file has been created successfully.")
    
    # Optional: Delete the file from the File API after processing
    print(f"Deleting file {uploaded_file.name} from the API...")
    genai.delete_file(uploaded_file.name)
    print("File deleted.")
    
    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process English Question Paper PDF to JSON")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_json", help="Path to output JSON file")
    args = parser.parse_args()

    process_question_paper(args.input_pdf, args.output_json)
