# Project Brief: Political Science Data Pipeline Implementation

### 🎯 Objective
Implement a standardized data processing pipeline for Bihar Board Class 12 Political Science Previous Year Questions (2021-2026), ensuring 100% structural and functional parity with the existing History, Geography, and Mathematics pipelines.

---

### 🔍 Phase 1: Knowledge Discovery
1. **Syllabus Research**: Perform a targeted web search for the official **NCERT Class 12 Political Science syllabus**.
2. **Chapter Extraction**: Compile a clean list of chapter titles. This list will serve as the ground truth for AI-driven annotation in Phase 3.

---

### 🏗️ Phase 2: Script Implementation
> **Crucial Requirement**: The following scripts must mirror the logic, naming conventions, and directory structures of the existing subject scripts.

1. **Extraction** (`batch_processing_political_science.py`):
   - Scope: All PDFs in `political_science_papers/`.
   - Action: Utilize the shared `process_question_paper` utility to generate raw JSON in `political_science_data/`.

2. **Annotation** (`batch_annotate_political_science.py`):
   - Logic: Feed raw questions to Gemini (using `models/gemini-3-flash-preview`).
   - Task: Map each question to the NCERT chapters identified in Phase 1.
   - Output: Annotated JSON in `political_science_data_annotated/`.

3. **Consolidation** (`merge_political_science.py`):
   - Action: Merge yearly annotated files into a single master database: `political_science_pro/political_science_all_years.json`.

4. **Multi-View Organization**:
   - `split_political_science_by_chapter.py`: Generate chapter-specific JSON files.
   - `split_political_science_by_type.py`: Generate type-specific JSON files (Objective, Short, Long).
   - `split_political_science_types_by_chapters.py`: Generate granular type-chapter matrices.

---

### 🚀 Phase 3: Pipeline Execution
> [!IMPORTANT]
> The following commands **MUST** be executed sequentially. Each script depends on the output of the previous one. An agent should request user permission for the entire sequence at once before starting.

```powershell
python batch_processing_political_science.py
python batch_annotate_political_science.py
python merge_political_science.py
python split_political_science_by_chapter.py
python split_political_science_by_type.py
python split_political_science_types_by_chapters.py
```

---

### 📝 Phase 4: Finalization
1. **Documentation**: Update `README.md` to document the new Political Science scripts.
2. **Version Control**: Stage and commit changes.

### ⚠️ Technical Guardrails
- **Maintain Consistency**: Follow the exactly same JSON structure and logging format as other subjects.
- **Reference Existing Code**: Treat `batch_processing_mathematics.py` and `batch_annotate_history.py` as primary templates.
