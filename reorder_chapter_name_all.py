import json
import pathlib
from collections import OrderedDict

def reorder_chapter_name_all_files(folder_path):
    folder = pathlib.Path(folder_path)
    files = list(folder.glob('*.json'))
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        new_data = []
        for q in data:
            if 'chapter' in q and 'chapter_name' in q:
                new_q = OrderedDict()
                for k, v in q.items():
                    new_q[k] = v
                    if k == 'chapter':
                        new_q['chapter_name'] = q['chapter_name']
                new_data.append(new_q)
            else:
                new_data.append(q)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        print(f"Reordered chapter_name for: {file_path.name}")

if __name__ == "__main__":
    reorder_chapter_name_all_files('biology_data_annotated')
