# Project Brief: Music Data Pipeline Implementation

### 🎯 Objective
Implement a standardized data processing pipeline for Bihar Board Class 12 Music Previous Year Questions (2021-2026), ensuring 100% structural and functional parity with the existing History, Geography, and Mathematics pipelines.

---

### 🔍 Phase 1: Knowledge Discovery
1. **Syllabus Research**: Perform a targeted web search for the official **Bihar Board Class 12 Music syllabus**.
2. **Chapter Extraction**: Compile a clean list of key topics or chapters. This list will serve as the ground truth for AI-driven annotation in Phase 3.

---

### 🏗️ Phase 2: Script Implementation
> **Crucial Requirement**: The following scripts must mirror the logic, naming conventions, and directory structures of the existing subject scripts.

1. **Extraction** (`batch_processing_music.py`):
   - Scope: All PDFs in `music_papers/`.
   - Action: Utilize the shared `process_question_paper` utility to generate raw JSON in `music_data/`.

2. **Annotation** (`batch_annotate_music.py`):
   - Logic: Feed raw questions to Gemini (using `models/gemini-2.5-pro`).
   - Task: Map each question to the topics identified in Phase 1.
   - Output: Annotated JSON in `music_data_annotated/`.

3. **Consolidation** (`merge_music.py`):
   - Action: Merge yearly annotated files into a single master database: `music_pro/music_all_years.json`.

4. **Multi-View Organization**:
   - `split_music_by_chapter.py`: Generate topic-specific JSON files.
   - `split_music_by_type.py`: Generate type-specific JSON files (Objective, Short, Long).
   - `split_music_types_by_chapters.py`: Generate granular type-topic matrices.

---

### 🚀 Phase 3: Pipeline Execution
> [!IMPORTANT]
> The following commands **MUST** be executed sequentially. Each script depends on the output of the previous one. An agent should request user permission for the entire sequence at once before starting.

```powershell
python batch_processing_music.py
python batch_annotate_music.py
python merge_music.py
python split_music_by_chapter.py
python split_music_by_type.py
python split_music_types_by_chapters.py
```

---

### 📝 Phase 4: Finalization
1. **Documentation**: Update `README.md` to document the new Music scripts.
2. **Version Control**: Stage and commit changes.

### ⚠️ Technical Guardrails
- **Maintain Consistency**: Follow the exactly same JSON structure and logging format as other subjects.
- **Reference Existing Code**: Treat `batch_processing_mathematics.py` and `batch_annotate_history.py` as primary templates.
