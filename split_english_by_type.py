import os
import json
from typing import Dict, List, Any


def normalize_type(type_value: str) -> str:
    if not type_value:
        return "unknown"
    
    type_lower = type_value.lower().strip()
    
    # English specific types
    valid_types = [
        "objective", "essay", "explanation", "letter_application", 
        "short_answer", "long_answer", "passage_comprehension", "precis"
    ]
    
    if type_lower in valid_types:
        return type_lower
    else:
        # Fallback for unexpected variations if any, though extraction script is strict
        return "unknown"


def main() -> None:
    source_path = os.path.join("english_pro", "english_all_years.json")
    output_dir = "english_pro_types"
    os.makedirs(output_dir, exist_ok=True)

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Expected top-level object keyed by year.")

    types_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for year, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            
            question_type = normalize_type(item.get("type", ""))
            
            if question_type not in types_data:
                types_data[question_type] = {}
            types_data[question_type].setdefault(year, []).append(item)

    manifest = []
    for type_name, year_map in types_data.items():
        try:
            ordered_years = sorted(year_map.keys(), key=lambda y: int(y))
        except ValueError:
            ordered_years = sorted(year_map.keys())
        ordered_obj = {y: year_map[y] for y in ordered_years}

        filename = f"type-{type_name}.json"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(ordered_obj, f, ensure_ascii=False, indent=2)

        total = sum(len(v) for v in year_map.values())
        manifest.append({
            "type": type_name, 
            "file": filename, 
            "total_items": total, 
            "years": len(year_map)
        })

    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(types_data)} type files to {output_dir}")
    for entry in manifest:
        print(f"{entry['type']}: {entry['total_items']} items across {entry['years']} years")


if __name__ == "__main__":
    main()
