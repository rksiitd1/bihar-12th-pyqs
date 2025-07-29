import json
import pathlib
import os

def extract_short_questions():
    """
    Extract all short answer questions from chemistry data files and save them in a single file
    """
    # Create extracts folder
    extracts_folder = pathlib.Path("extracts")
    extracts_folder.mkdir(exist_ok=True)
    
    # Path to chemistry data folder
    chemistry_data_folder = pathlib.Path("chemistry_data")
    
    # Dictionary to store all short questions organized by year
    all_short_questions = {}
    
    # Process each chemistry data file
    for json_file in chemistry_data_folder.glob("chem_*.json"):
        year = json_file.stem.split("_")[1]  # Extract year from filename (e.g., "chem_2015.json" -> "2015")
        
        print(f"Processing {json_file.name}...")
        
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract short answer questions
        short_questions = []
        for item in data:
            if item.get("type") == "short_answer":
                short_question = {
                    "id": item.get("id", ""),
                    "question": item.get("question", ""),
                    "prashna": item.get("prashna", "")
                }
                # Add sub-questions if they exist
                if "sub_questions" in item:
                    short_question["sub_questions"] = item["sub_questions"]
                if "anuprashna" in item:
                    short_question["anuprashna"] = item["anuprashna"]
                short_questions.append(short_question)
        
        # Store short questions for this year
        all_short_questions[year] = short_questions
        
        print(f"  ✅ Extracted {len(short_questions)} short questions from {year}")
    
    # Save all short questions to a single file
    output_file = extracts_folder / "chemistry_short_questions_all_years.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_short_questions, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Extraction complete! All short questions saved in '{output_file.name}'")
    
    return all_short_questions

def create_summary(all_short_questions):
    """
    Create a summary file with statistics about extracted short questions
    """
    extracts_folder = pathlib.Path("extracts")
    summary_data = {}
    
    total_questions = 0
    for year, questions in all_short_questions.items():
        count = len(questions)
        total_questions += count
        summary_data[year] = {
            "total_questions": count
        }
    
    # Add overall summary
    summary_data["overall"] = {
        "total_questions": total_questions,
        "total_years": len(all_short_questions),
        "years_covered": sorted(all_short_questions.keys())
    }
    
    # Save summary
    summary_file = extracts_folder / "short_extraction_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Summary saved to {summary_file}")
    
    # Print summary to console
    print("\n📋 Extraction Summary:")
    print("-" * 50)
    for year in sorted(all_short_questions.keys()):
        count = len(all_short_questions[year])
        print(f"Year {year}: {count} short questions")
    print("-" * 50)
    print(f"Total: {total_questions} short questions across {len(all_short_questions)} years")

if __name__ == "__main__":
    all_short_questions = extract_short_questions()
    create_summary(all_short_questions) 