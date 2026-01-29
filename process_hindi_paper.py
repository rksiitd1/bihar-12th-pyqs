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
    Your task is to act as an expert data extraction engine. You will receive a PDF file of a Class 12 Hindi Question Paper. You must meticulously extract all questions and convert them into a single, clean JSON array.

    Follow these instructions precisely:

    1.  **JSON Structure**: The output must be a JSON array where each element is an object representing a single question.
    2.  **Required Fields for All Questions**:
        - `id`: A unique string identifier. For each question type, numbering must start from 1. For example: "objective_1", "objective_2", ... "essay_1", "short_1", "long_1", etc. The numbering for each type must always start at 1, regardless of their order in the paper.
        - If two or more questions are given as alternatives (using "or"/"athva") under the same question number, represent them as `long_1_1`, `long_1_2`, etc. (or `short_5_1`, `short_5_2`, etc.) in the `id` field, where the main number is the question number and the sub-number distinguishes the alternatives.
        - `type`: The question type as a string. Use these exact keys:
            - `objective` (Vastunisth Prashna)
            - `essay` (Nibandh)
            - `explanation` (Saprasang Vyakhya)
            - `letter_writing` (Patra Lekhan)
            - `short_answer` (Laghu Uttariya)
            - `long_answer` (Dirgha Uttariya)
            - `summary` (Saransh/Bhavarth)
            - `translation` (Anuvad)
            - `comprehension` (Gadyansh/Sankshepan)
        - `question`: The full text of the question (in Hindi, as it appears).
        - `instructions`: Any specific instructions for this question (e.g., "Answer any 5", "Write in approx 250 words").

    3.  **Fields for "objective" Type Questions**:
        - `options`: An object with keys "A", "B", "C", "D" containing the option text.
        - `answer`: The correct answer option key if marked or obvious (optional).

    4.  **Fields for Questions (both "short_answer" and "long_answer") with Sub-Questions**:
        - If a question contains sub-questions, include:
            - `sub_questions`: An object containing the sub-questions associated with the main question.

    5.  **Accuracy**: Ensure the text for questions, options, and sub-questions is extracted exactly as it appears in the document. Preserve all Hindi text accurately.

    The PDF file is provided. Begin processing now and generate only the JSON array as your output.
    """)

    return [
        {'text': prompt},
        {'file_data': {
            'mime_type': 'application/pdf',
            'file_uri': uploaded_file_uri
        }}
    ]

def process_hindi_question_paper(input_pdf_path: str, output_json_path: str):
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
    # Safety settings to avoid blocking educational content
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    response = model.generate_content(prompt_parts, safety_settings=safety_settings)

    # Step 4: Clean and parse the response
    print("Cleaning and parsing the JSON response...")
    
    # Check if response was blocked by safety filters
    if not response.candidates or not response.candidates[0].content.parts:
        print("\n--- ERROR: Response blocked by Gemini API ---")
        if response.candidates and response.candidates[0].safety_ratings:
            print("Safety Ratings:")
            for rating in response.candidates[0].safety_ratings:
                print(f"  {rating.category}: {rating.probability}")
        if hasattr(response, 'prompt_feedback'):
            print(f"Prompt Feedback: {response.prompt_feedback}")
        print("\nThis PDF may contain content flagged by safety filters.")
        print("Try manually reviewing the PDF or using a different extraction method.")
        print("-" * 50)
        return  # Exit without writing a file
    
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
        print("\n--- Raw Model Response (if available): ---")
        try:
            print(response.text)
        except:
            print("Could not access response.text")
        return

    # Step 5: Write the structured data to the output file
    output_path = pathlib.Path(output_json_path)
    output_path.parent.mkdir(exist_ok=True, parents=True) # Ensure dir exists
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
    pass
