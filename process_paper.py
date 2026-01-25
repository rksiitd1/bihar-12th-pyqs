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
    Your task is to act as an expert data extraction engine. You will receive a PDF file of a question paper. You must meticulously extract all questions and convert them into a single, clean JSON array.

    Follow these instructions precisely:

    1.  **JSON Structure**: The output must be a JSON array where each element is an object representing a single question.
    2.  **Required Fields for All Questions**:
        - `id`: A unique string identifier. For each question type, numbering must start from 1. For example: "obj_1", "obj_2", ... "short_1", "short_2", ... "long_1", "long_2", etc. The numbering for each type must always start at 1, regardless of their order in the paper.
        - If two or more questions are given as alternatives (using "or"/"athva") under the same question number, represent them as `long_1_1`, `long_1_2`, etc. (or `short_5_1`, `short_5_2`, etc.) in the `id` field, where the main number is the question number and the sub-number distinguishes the alternatives.
        - `type`: The question type as a string ("objective", "short_answer", "long_answer").
        - `question`: The full English text of the question.
        - `prashna`: The full Hindi text of the question.

    3.  **If a question, option, or sub-question is present only in one language (either English or Hindi), you MUST translate it to the other language and fill both fields.**
        - Use accurate, context-aware translation. Preserve scientific/technical terms and LaTeX formatting.
        - For example, if only the Hindi version is present, translate it to English for the `question` field, and vice versa.

    4.  **Fields for "objective" Type Questions**:
        - `options`: An object containing the English options, with keys "A", "B", "C", "D".
        - `vikalpa`: An object containing the Hindi options, with keys "A", "B", "C", "D".
        - If options are present in only one language, translate them to the other language as above.

    5.  **Fields for Questions (both "short_answer" and "long_answer") with Sub-Questions**:
        - If a question (of type "short_answer" or "long_answer") contains sub-questions, include:
            - `sub_questions`: An object containing the English sub-questions, with keys like "A", "B".
            - `anuprashna`: An object containing the Hindi sub-questions, with keys like "A", "B".
        - If sub-questions are present in only one language, translate them to the other language as above.

    6.  **LaTeX Formatting (CRITICAL)**:
        - You MUST convert all mathematical, chemical, and scientific notations into proper LaTeX format.
        - **Examples**:
          - `F₁` should be `$F_1$`.
          - `H₂O` should be `$H_2O$`.
          - `β-galactosidase` should be `$\\beta$-galactosidase`.
          - `2 x 2¹/₂ = 5` should be `$2 \\times 2^{1/2} = 5$`.

    7.  **Accuracy**: Ensure the text for questions, options, and sub-questions is extracted exactly as it appears in the document, for both languages. Do not add any text that is not present in the source PDF, except for accurate translations as described above.

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


# --- Interactive Interface ---

def get_available_files():
    """Get all available PDF files from subject folders."""
    subjects = ['biology', 'chemistry', 'mathematics', 'physics']
    available_files = []
    
    for subject in subjects:
        papers_folder = pathlib.Path(f"{subject}_papers")
        if papers_folder.exists():
            pdf_files = list(papers_folder.glob("*.pdf"))
            for pdf_file in pdf_files:
                available_files.append({
                    'path': pdf_file,
                    'subject': subject,
                    'name': pdf_file.name
                })
    
    return available_files

def create_data_folder(subject):
    """Create data folder for the subject if it doesn't exist."""
    data_folder = pathlib.Path(f"{subject}_data")
    data_folder.mkdir(exist_ok=True)
    return data_folder

if __name__ == "__main__":
    print("Question Paper Processor")
    print("=" * 50)
    
    # Get all available files
    files = get_available_files()
    
    if not files:
        print("No PDF files found in any subject folders!")
        exit(1)
    
    # Display available files in table format
    print(f"\nFound {len(files)} PDF files:")
    print("=" * 80)
    print(f"{'No.':<4} {'Subject':<12} {'Year':<6} {'Filename':<30} {'Status':<10}")
    print("-" * 80)
    
    for i, file_info in enumerate(files, 1):
        # Extract year from filename (assuming format like bio_2023.pdf)
        filename = file_info['name']
        year = filename.split('_')[-1].replace('.pdf', '') if '_' in filename else 'N/A'
        
        # Check if output already exists
        data_folder = pathlib.Path(f"{file_info['subject']}_data")
        json_filename = file_info['path'].stem + ".json"
        json_path = data_folder / json_filename
        status = "✓ Done" if json_path.exists() else "Pending"
        
        print(f"{i:<4} {file_info['subject']:<12} {year:<6} {filename:<30} {status:<10}")
    
    print("=" * 80)
    
    # Get user selection
    while True:
        try:
            choice = input(f"\nEnter file number (1-{len(files)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Goodbye!")
                exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Process the selected file
    print(f"\nProcessing: {selected_file['name']}")
    print(f"Subject: {selected_file['subject']}")
    
    # Create output folder and path
    data_folder = create_data_folder(selected_file['subject'])
    json_filename = selected_file['path'].stem + ".json"
    json_path = data_folder / json_filename
    
    print(f"Output will be saved to: {json_path}")
    
    # Confirm processing
    confirm = input("\nProceed with processing? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Processing cancelled.")
        exit(0)
    
    # Process the file
    try:
        process_question_paper(str(selected_file['path']), str(json_path))
        print(f"\n✓ Successfully processed {selected_file['name']}")
        print(f"✓ Output saved to: {json_path}")
    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")