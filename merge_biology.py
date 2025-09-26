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
    source_dir = "biology_data_annotated"
    output_dir = "biology_pro"
    os.makedirs(output_dir, exist_ok=True)

    input_files = sorted(glob.glob(os.path.join(source_dir, "bio_*.json")))
    merged: List[Dict[str, Any]] = []
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

        merged.extend(items)
        per_file_counts[os.path.basename(file_path)] = len(items)

    output_path = os.path.join(output_dir, "biology_all_years.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Wrote {output_path} with {len(merged)} items")
    for name in sorted(per_file_counts):
        print(f"{name}: {per_file_counts[name]}")


if __name__ == "__main__":
    main()


