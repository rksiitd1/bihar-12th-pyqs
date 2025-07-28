import time
from process_paper import process_question_paper
import pathlib

def main():
    # List of years to process, in descending order
    years = list(range(2025, 2008, -1))  # 2017 to 2009
    input_folder = pathlib.Path("physics_papers")
    output_folder = pathlib.Path("physics_data")
    output_folder.mkdir(exist_ok=True)

    for year in years:
        input_pdf = input_folder / f"phy_{year}.pdf"
        output_json = output_folder / f"phy_{year}.json"
        
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