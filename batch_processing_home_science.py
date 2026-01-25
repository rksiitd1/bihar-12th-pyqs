import time
from process_paper import process_question_paper
import pathlib

def main():
    # List of years to process
    years = list(range(2026, 2020, -1))  # 2026 to 2021
    input_folder = pathlib.Path("home_science_papers")
    output_folder = pathlib.Path("home_science_data")
    output_folder.mkdir(exist_ok=True)

    for year in years:
        input_pdf = input_folder / f"hsci_{year}.pdf"
        output_json = output_folder / f"hsci_{year}.json"
        
        # Check if input file exists
        if not input_pdf.exists():
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
