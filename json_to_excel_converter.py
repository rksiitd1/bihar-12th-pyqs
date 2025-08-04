import json
import pandas as pd
from pathlib import Path

def convert_json_to_excel(json_file_path, excel_file_path=None):
    """
    Convert a JSON file containing physics questions to an Excel file.
    
    Args:
        json_file_path (str): Path to the input JSON file
        excel_file_path (str, optional): Path for the output Excel file. 
                                       If not provided, will use the same name as JSON with .xlsx extension
    """
    # If no output path is provided, create one based on input path
    if excel_file_path is None:
        excel_file_path = str(Path(json_file_path).with_suffix('.xlsx'))
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process the data into a format suitable for Excel
    processed_data = []
    for item in data:
        # Create a new dictionary for each question
        row = {
            'ID': item.get('id', ''),
            'Type': item.get('type', ''),
            'Chapter': item.get('chapter', ''),
            'Chapter Name': item.get('chapter_name', ''),
            'Topic': item.get('topic', ''),
            'Topic Name': item.get('topic_name', ''),
            'Question (English)': item.get('question', ''),
            'Question (Hindi)': item.get('prashna', '')
        }
        
        # Add options if they exist
        options = item.get('options', {})
        vikalpa = item.get('vikalpa', {})
        
        for opt in ['A', 'B', 'C', 'D']:
            row[f'Option {opt}'] = options.get(opt, '')
            row[f'Vikalpa {opt}'] = vikalpa.get(opt, '')
        
        # Add answer if it exists
        row['Answer'] = item.get('answer', '')
        row['Answer (Hindi)'] = item.get('uttar', '')
        
        # Add explanation if it exists
        row['Explanation'] = item.get('explanation', '')
        
        processed_data.append(row)
    
    # Create a DataFrame and save to Excel
    df = pd.DataFrame(processed_data)
    
    # Write to Excel with auto-adjusting column widths
    with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Physics Questions')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Physics Questions']
        for i, col in enumerate(df.columns):
            # Find the maximum length in the column
            max_length = max(
                df[col].astype(str).apply(len).max(),  # Max length in the column
                len(str(col))  # Length of column name
            )
            # Set column width (adding a little extra space)
            worksheet.set_column(i, i, min(max_length + 2, 50))
    
    print(f"Successfully converted {len(processed_data)} questions to {excel_file_path}")

if __name__ == "__main__":
    # Example usage
    input_json = r"c:\Users\vidya\gurukulam\0\pushtak\pyqs\physics_data_annotated\phy_2009.json"
    convert_json_to_excel(input_json)
