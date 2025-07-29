import json
import pathlib
import os

def extract_objective_questions():
    """
    Extract all objective questions from chemistry data files and save them in a single file
    """
    # Create extracts folder
    extracts_folder = pathlib.Path("extracts")
    extracts_folder.mkdir(exist_ok=True)
    
    # Path to chemistry data folder
    chemistry_data_folder = pathlib.Path("chemistry_data")
    
    # Dictionary to store all objective questions organized by year
    all_objective_questions = {}
    
    # Process each chemistry data file
    for json_file in chemistry_data_folder.glob("chem_*.json"):
        year = json_file.stem.split("_")[1]  # Extract year from filename (e.g., "chem_2015.json" -> "2015")
        
        print(f"Processing {json_file.name}...")
        
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract objective questions
        objective_questions = []
        for item in data:
            if item.get("type") == "objective":
                objective_question = {
                    "id": item.get("id", ""),
                    "question": item.get("question", ""),
                    "prashna": item.get("prashna", "")
                }
                # Add options if they exist
                if "options" in item:
                    objective_question["options"] = item["options"]
                if "answer" in item:
                    objective_question["answer"] = item["answer"]
                objective_questions.append(objective_question)
        
        # Store objective questions for this year
        all_objective_questions[year] = objective_questions
        
        print(f"  ✅ Extracted {len(objective_questions)} objective questions from {year}")
    
    # Save all objective questions to a single file
    output_file = extracts_folder / "chemistry_objective_questions_all_years.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_objective_questions, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Extraction complete! All objective questions saved in '{output_file.name}'")
    
    return all_objective_questions

def create_summary(all_objective_questions):
    """
    Create a summary file with statistics about extracted objective questions
    """
    extracts_folder = pathlib.Path("extracts")
    summary_data = {}
    
    total_questions = 0
    for year, questions in all_objective_questions.items():
        count = len(questions)
        total_questions += count
        summary_data[year] = {
            "total_questions": count
        }
    
    # Add overall summary
    summary_data["overall"] = {
        "total_questions": total_questions,
        "total_years": len(all_objective_questions),
        "years_covered": sorted(all_objective_questions.keys())
    }
    
    # Save summary
    summary_file = extracts_folder / "objective_extraction_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Summary saved to {summary_file}")
    
    # Print summary to console
    print("\n📋 Extraction Summary:")
    print("-" * 50)
    for year in sorted(all_objective_questions.keys()):
        count = len(all_objective_questions[year])
        print(f"Year {year}: {count} objective questions")
    print("-" * 50)
    print(f"Total: {total_questions} objective questions across {len(all_objective_questions)} years")

if __name__ == "__main__":
    all_objective_questions = extract_objective_questions()
    create_summary(all_objective_questions) 