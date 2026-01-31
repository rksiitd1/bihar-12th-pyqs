import os
import json
import pathlib
import random

HINDI_CHAPTERS = [
    # Prose (Digant Bhag 2 - Gadyakhand)
    "Baat Cheet",
    "Usne Kaha Tha",
    "Sampoorna Kranti",
    "Ardhanarishwar",
    "Roz",
    "Ek Lekh Aur Ek Patra",
    "O Sadanira",
    "Sipahi Ki Maa",
    "Pragit Aur Samaj",
    "Joothan",
    "Hanste Hue Mera Akelapan",
    "Tirichh",
    "Shiksha",

    # Poetry (Digant Bhag 2 - Kavyakhand)
    "Kadbak",
    "Pad (Surdas)",
    "Pad (Tulsidas)",
    "Chhappay",
    "Kavitt",
    "Tumul Kolahal Kalah Mein",
    "Putra Viyog",
    "Usha",
    "Jaan-Jaan Ka Chehra Ek",
    "Adhinayak",
    "Pyare Nanhe Bete Ko",
    "Haar-Jeet",
    "Gaon Ka Ghar",

    # Supplementary (Pratipurti)
    "Rassi Ka Tukda",
    "Clerk Ki Maut",
    "Peshgi"
]

def main():
    print("Batch Hindi Question Annotator (Dummy - Random + Grammar)")
    print("="*40)
    
    data_folder = pathlib.Path("hindi_data")
    out_folder = pathlib.Path("hindi_data_annotated")
    out_folder.mkdir(exist_ok=True)
    
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in hindi_data/!")
        return

    # Keywords in Hindi or English transliteration that imply grammar/composition
    grammar_keywords = [
        "nibandh", "letter", "patra", "sankshepan", "precis", 
        "gadyansh", "passage", "anuvad", "translate", "vyakaran", "grammar"
    ]

    for fpath in files:
        # Filter check (optional, matching other scripts)
        # Assuming we process everything if year logic isn't strictly enforced here logic
        
        out_path = out_folder / fpath.name
        
        print(f"Processing (Dummy): {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        annotated = []
        for q in questions:
            q_type = q.get("type", "").lower()
            
            is_grammar = False
            for kw in grammar_keywords:
                if kw in q_type:
                    is_grammar = True
                    break
            
            if is_grammar:
                chapter = "Vyakaran"
            else:
                chapter = random.choice(HINDI_CHAPTERS)
            
            new_q = {}
            for k, v in q.items():
                new_q[k] = v
                if k == "type":
                    new_q["chapter_name"] = chapter
            
            if "chapter_name" not in new_q:
                new_q["chapter_name"] = chapter
                
            annotated.append(new_q)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(annotated, f, indent=4, ensure_ascii=False)
        print(f"✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    main()
