import os
import json
import glob
from typing import List, Dict, Any


def read_items_from_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("questions", "data", "items", "records"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def main() -> None:
    source_dir = "mathematics_data_annotated"
    output_dir = "mathematics_pro"
    os.makedirs(output_dir, exist_ok=True)

    input_files = sorted(glob.glob(os.path.join(source_dir, "math_*.json")))
    grouped_by_year: Dict[str, List[Dict[str, Any]]] = {}
    per_file_counts: Dict[str, int] = {}

    for file_path in input_files:
        try:
            items = read_items_from_file(file_path)
        except json.JSONDecodeError as e:
            print(f"Failed to parse {file_path}: {e}")
            continue
        except OSError as e:
            print(f"Failed to read {file_path}: {e}")
            continue

        base = os.path.basename(file_path)
        year = "".join(ch for ch in base if ch.isdigit())
        # Fallback if we couldn't parse digits
        if not year:
            year = base
        grouped_by_year.setdefault(year, []).extend(items)
        per_file_counts[base] = len(items)

    # Sort the years numerically when possible for stable output
    def year_sort_key(k: str) -> Any:
        try:
            return int(k)
        except ValueError:
            return k

    ordered_years = sorted(grouped_by_year.keys(), key=year_sort_key)
    ordered_obj: Dict[str, List[Dict[str, Any]]] = {y: grouped_by_year[y] for y in ordered_years}

    output_path = os.path.join(output_dir, "mathematics_all_years.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=2)

    total_items = sum(len(v) for v in grouped_by_year.values())
    print(f"Wrote {output_path} with {total_items} items across {len(grouped_by_year)} years")
    for name in sorted(per_file_counts):
        print(f"{name}: {per_file_counts[name]}")


if __name__ == "__main__":
    main()
