import json
import pathlib
from collections import OrderedDict

def reorder_chapter_name_after_chapter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    new_data = []
    for q in data:
        if 'chapter' in q and 'chapter_name' in q:
            new_q = OrderedDict()
            for k, v in q.items():
                new_q[k] = v
                if k == 'chapter':
                    # Insert chapter_name immediately after chapter
                    new_q['chapter_name'] = q['chapter_name']
            new_data.append(new_q)
        else:
            new_data.append(q)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    print(f"Reordered chapter_name for: {file_path}")

if __name__ == "__main__":
    # Change the path below to process all files in a folder if needed
    reorder_chapter_name_after_chapter('biology_data_annotated/bio_2009.json')
