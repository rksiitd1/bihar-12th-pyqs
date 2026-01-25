import os
import json
import re
from typing import Dict, List, Any


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\-\_\s]", "", value)
    value = re.sub(r"[\s\-]+", "-", value)
    return value or "unknown"


def main() -> None:
    source_path = os.path.join("music_pro", "music_all_years.json")
    output_dir = "music_pro_chapters"
    os.makedirs(output_dir, exist_ok=True)

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Expected top-level object keyed by year.")

    # Map: chapter_key -> { year -> [items] }
    chapters: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for year, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            # Prefer explicit chapter identifier, fallback to chapter_name
            chapter_id = item.get("chapter")
            if chapter_id is None or chapter_id == "":
                chapter_id = item.get("chapter_name")
            if chapter_id is None or chapter_id == "":
                chapter_id = "unknown"

            chapter_key = str(chapter_id)
            if chapter_key not in chapters:
                chapters[chapter_key] = {}
            chapters[chapter_key].setdefault(year, []).append(item)

    # Write one file per chapter, preserving dict-of-years structure
    manifest = []
    for chapter_key, year_map in chapters.items():
        # order years numerically when possible
        try:
            ordered_years = sorted(year_map.keys(), key=lambda y: int(y))
        except ValueError:
            ordered_years = sorted(year_map.keys())
        ordered_obj = {y: year_map[y] for y in ordered_years}

        filename = f"chapter-{slugify(chapter_key)}.json"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(ordered_obj, f, ensure_ascii=False, indent=2)

        total = sum(len(v) for v in year_map.values())
        manifest.append({"chapter": chapter_key, "file": filename, "total_items": total, "years": len(year_map)})

    # Also write a manifest for convenience
    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(chapters)} chapter files to {output_dir}")


if __name__ == "__main__":
    main()
