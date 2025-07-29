import json
import pathlib
import os

def extract_long_questions():
    """
    Extract all long answer questions from chemistry data files and save them in a single file
    """
    # Create extracts folder
    extracts_folder = pathlib.Path("extracts")
    extracts_folder.mkdir(exist_ok=True)
    
    # Path to chemistry data folder
    chemistry_data_folder = pathlib.Path("chemistry_data")
    
    # Dictionary to store all long questions organized by year
    all_long_questions = {}
    
    # Process each chemistry data file
    for json_file in chemistry_data_folder.glob("chem_*.json"):
        year = json_file.stem.split("_")[1]  # Extract year from filename (e.g., "chem_2015.json" -> "2015")
        
        print(f"Processing {json_file.name}...")
        
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract long answer questions
        long_questions = []
        for item in data:
            if item.get("type") == "long_answer":
                long_question = {
                    "id": item.get("id", ""),
                    "question": item.get("question", ""),
                    "prashna": item.get("prashna", "")
                }
                
                # Add sub-questions if they exist
                if "sub_questions" in item:
                    long_question["sub_questions"] = item["sub_questions"]
                if "anuprashna" in item:
                    long_question["anuprashna"] = item["anuprashna"]
                
                long_questions.append(long_question)
        
        # Store long questions for this year
        all_long_questions[year] = long_questions
        
        print(f"  ✅ Extracted {len(long_questions)} long questions from {year}")
    
    # Save all long questions to a single file
    output_file = extracts_folder / "chemistry_long_questions_all_years.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_long_questions, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Extraction complete! All long questions saved in '{output_file.name}'")
    
    return all_long_questions

def create_summary(all_long_questions):
    """
    Create a summary file with statistics about extracted long questions
    """
    extracts_folder = pathlib.Path("extracts")
    summary_data = {}
    
    total_questions = 0
    for year, questions in all_long_questions.items():
        count = len(questions)
        total_questions += count
        summary_data[year] = {
            "total_questions": count
        }
    
    # Add overall summary
    summary_data["overall"] = {
        "total_questions": total_questions,
        "total_years": len(all_long_questions),
        "years_covered": sorted(all_long_questions.keys())
    }
    
    # Save summary
    summary_file = extracts_folder / "extraction_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Summary saved to {summary_file}")
    
    # Print summary to console
    print("\n📋 Extraction Summary:")
    print("-" * 50)
    for year in sorted(all_long_questions.keys()):
        count = len(all_long_questions[year])
        print(f"Year {year}: {count} long questions")
    print("-" * 50)
    print(f"Total: {total_questions} long questions across {len(all_long_questions)} years")

if __name__ == "__main__":
    all_long_questions = extract_long_questions()
    create_summary(all_long_questions) 