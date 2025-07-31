import json
import pathlib
from annotate_questions_with_chapters import CHAPTERS

def add_chapter_names(subject):
    chapters = CHAPTERS[subject]
    annotated_folder = pathlib.Path(f"{subject}_data_annotated")
    files = list(annotated_folder.glob("*.json"))
    if not files:
        print(f"No files found in {annotated_folder}/")
        return
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = False
        for q in data:
            chapter_num = q.get("chapter")
            if chapter_num is not None and "chapter_name" not in q:
                try:
                    idx = int(chapter_num) - 1
                    if 0 <= idx < len(chapters):
                        q["chapter_name"] = chapters[idx]
                        changed = True
                except Exception:
                    pass
        if changed:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Updated: {file.name}")
        else:
            print(f"No change needed: {file.name}")

if __name__ == "__main__":
    add_chapter_names("biology")
