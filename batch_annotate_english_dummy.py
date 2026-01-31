import os
import json
import pathlib
import random

ENGLISH_CHAPTERS = [
    # Flamingo (Prose)
    "The Last Lesson",
    "Lost Spring",
    "Deep Water",
    "The Rattrap",
    "Indigo",
    "Poets and Pancakes",
    "The Interview",
    "Going Places",

    # Flamingo (Poetry)
    "My Mother at Sixty-Six",
    "Keeping Quiet",
    "A Thing of Beauty",
    "A Roadside Stand",
    "Aunt Jennifer's Tigers",

    # Vistas
    "The Third Level",
    "The Tiger King",
    "Journey to the End of the Earth",
    "The Enemy",
    "On the Face of It",
    "Memories of Childhood"
]

def main():
    print("Batch English Question Annotator (Dummy - Random + Grammar)")
    print("="*40)
    
    data_folder = pathlib.Path("english_data")
    out_folder = pathlib.Path("english_data_annotated")
    out_folder.mkdir(exist_ok=True)
    
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in english_data/!")
        return

    grammar_keywords = ["essay", "letter", "precis", "comprehension", "passage", "grammar", "translate", "translation"]

    for fpath in files:
        # Filter for 2021-2026 check if desired, keeping consistent with other scripts
        try:
            year_str = fpath.stem.split('_')[-1]
            year = int(year_str)
            if not (2021 <= year <= 2026):
                continue
        except ValueError:
            pass 

        out_path = out_folder / fpath.name
        # Note: We overwrite existing files to ensure we apply the dummy logic everywhere if requested
        # Or you can check if out_path.exists() to skip. Let's overwrite for now to be safe.
        
        print(f"Processing (Dummy): {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        annotated = []
        for q in questions:
            q_type = q.get("type", "").lower()
            
            # Logic: If type suggests grammar/composition, assign "Grammar"
            # Otherwise, assign a random chapter from the book
            
            is_grammar = False
            for kw in grammar_keywords:
                if kw in q_type:
                    is_grammar = True
                    break
            
            if is_grammar:
                chapter = "Grammar"
            else:
                chapter = random.choice(ENGLISH_CHAPTERS)
            
            # Create new dict with chapter_name inserted after type
            new_q = {}
            for k, v in q.items():
                new_q[k] = v
                if k == "type":
                    new_q["chapter_name"] = chapter
            
            # Fallback if type wasn't found (should be there usually)
            if "chapter_name" not in new_q:
                new_q["chapter_name"] = chapter
            
            annotated.append(new_q)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(annotated, f, indent=4, ensure_ascii=False)
        print(f"✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    main()
