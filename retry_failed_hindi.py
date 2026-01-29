import time
from process_hindi_paper import process_hindi_question_paper
import pathlib

def main():
    """Retry only the failed years with enhanced error reporting."""
    
    # Years that failed in the batch run
    failed_years = [2022, 2021, 2020, 2019, 2017, 2012]
    
    input_folder = pathlib.Path("hindi_papers")
    output_folder = pathlib.Path("hindi_data")
    output_folder.mkdir(exist_ok=True)

    print("=" * 60)
    print("RETRY FAILED HINDI PAPERS - Enhanced Error Reporting")
    print("=" * 60)
    print(f"Attempting to process {len(failed_years)} failed years")
    print(f"Years: {failed_years}\n")

    success_count = 0
    failed_list = []

    for year in failed_years:
        input_pdf = input_folder / f"hin-{year}.pdf"
        output_json = output_folder / f"hindi_{year}.json"
        
        # Check if input file exists
        if not input_pdf.exists():
            print(f"⚠️  Skipping {year} - PDF not found")
            failed_list.append((year, "PDF not found"))
            continue
            
        # Check if already processed
        if output_json.exists():
            print(f"✓  {year} - Already successfully processed")
            success_count += 1
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing Year {year}")
        print(f"{'='*60}")
        print(f"Input:  {input_pdf}")
        print(f"Output: {output_json}")
        
        start = time.time()
        try:
            process_hindi_question_paper(str(input_pdf), str(output_json))
            
            # Verify the output was created
            if output_json.exists():
                print(f"✓  SUCCESS - {year} processed successfully")
                success_count += 1
            else:
                print(f"❌ FAILED - {year} - No output file created")
                failed_list.append((year, "No output file"))
                
        except Exception as e:
            print(f"❌ FAILED - {year} - Exception: {e}")
            failed_list.append((year, str(e)))
            
        end = time.time()
        print(f"⏱️  Time: {end - start:.2f}s ({(end - start)/60:.2f} min)")

    # Final Summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"✓  Successful: {success_count}/{len(failed_years)}")
    print(f"❌ Failed:     {len(failed_list)}/{len(failed_years)}")
    
    if failed_list:
        print(f"\nFailed Years:")
        for year, reason in failed_list:
            print(f"  - {year}: {reason}")

if __name__ == "__main__":
    main()
