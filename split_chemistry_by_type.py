import os
import json
from typing import Dict, List, Any


def normalize_type(type_value: str) -> str:
    """Normalize question type to standard names."""
    if not type_value:
        return "unknown"
    
    type_lower = type_value.lower().strip()
    
    # Map various possible type names to standard ones
    if type_lower in ["objective", "mcq", "multiple choice", "multiple_choice"]:
        return "objective"
    elif type_lower in ["short", "short answer", "short_answer", "sa"]:
        return "short"
    elif type_lower in ["long", "long answer", "long_answer", "la", "descriptive"]:
        return "long"
    else:
        return "unknown"


def main() -> None:
    source_path = os.path.join("chemistry_pro", "chemistry_all_years.json")
    output_dir = "chemistry_pro_types"
    os.makedirs(output_dir, exist_ok=True)

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Expected top-level object keyed by year.")

    # Map: type -> { year -> [items] }
    types_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for year, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Get and normalize the type
            question_type = normalize_type(item.get("type", ""))
            
            if question_type not in types_data:
                types_data[question_type] = {}
            types_data[question_type].setdefault(year, []).append(item)

    # Write one file per type, preserving dict-of-years structure
    manifest = []
    for type_name, year_map in types_data.items():
        # Order years numerically when possible
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

    # Also write a manifest for convenience
    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(types_data)} type files to {output_dir}")
    for entry in manifest:
        print(f"{entry['type']}: {entry['total_items']} items across {entry['years']} years")


if __name__ == "__main__":
    main()