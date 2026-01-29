import time
from process_english_paper import process_question_paper
import pathlib
from dotenv import load_dotenv

# Load key from .env
load_dotenv()

def main():
    # List of years to process (2021-2026)
    years = list(range(2026, 2008, -1))
    input_folder = pathlib.Path("english_papers")
    output_folder = pathlib.Path("english_data")
    output_folder.mkdir(exist_ok=True)

    for year in years:
        # Note: English papers use hyphens (e.g., eng-2021.pdf)
        input_pdf = input_folder / f"eng-{year}.pdf"
        output_json = output_folder / f"eng_{year}.json"
        
        # Check if input file exists
        if not input_pdf.exists():
            # Try with underscore just in case
            input_pdf_alt = input_folder / f"eng_{year}.pdf"
            if input_pdf_alt.exists():
                input_pdf = input_pdf_alt
            else:
                print(f"⚠️  Skipping {input_pdf.name} -> file not found")
                continue
            
        # Check if output file already exists
        if output_json.exists():
            print(f"⏭️  Skipping {input_pdf.name} -> {output_json.name} (already processed)")
            continue
            
        print(f"\nProcessing {input_pdf} -> {output_json}")
        start = time.time()
        try:
            process_question_paper(str(input_pdf), str(output_json))
        except Exception as e:
            print(f"Error processing {input_pdf}: {e}")
        end = time.time()
        print(f"⏱️  Time taken for {input_pdf.name}: {end - start:.2f} seconds ({(end - start)/60:.2f} minutes)")

if __name__ == "__main__":
    main()
