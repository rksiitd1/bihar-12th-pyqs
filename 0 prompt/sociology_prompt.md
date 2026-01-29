# Project Brief: Sociology Data Pipeline Implementation

### 🎯 Objective
Implement a standardized data processing pipeline for Bihar Board Class 12 Sociology Previous Year Questions (2021-2026), ensuring 100% structural and functional parity with the existing History, Geography, and Mathematics pipelines.

---

### 🔍 Phase 1: Knowledge Discovery
1. **Syllabus Research**: Perform a targeted web search for the official **NCERT Class 12 Sociology syllabus**.
2. **Chapter Extraction**: Compile a clean list of chapter titles. This list will serve as the ground truth for AI-driven annotation in Phase 3.

---

### 🏗️ Phase 2: Script Implementation
> **Crucial Requirement**: The following scripts must mirror the logic, naming conventions, and directory structures of the existing subject scripts.

1. **Extraction** (`batch_processing_sociology.py`):
   - Scope: All PDFs in `sociology_papers/`.
   - Action: Utilize the shared `process_question_paper` utility to generate raw JSON in `sociology_data/`.

2. **Annotation** (`batch_annotate_sociology.py`):
   - Logic: Feed raw questions to Gemini (using `models/gemini-2.5-pro`).
   - Task: Map each question to the NCERT chapters identified in Phase 1.
   - Output: Annotated JSON in `sociology_data_annotated/`.

3. **Consolidation** (`merge_sociology.py`):
   - Action: Merge yearly annotated files into a single master database: `sociology_pro/sociology_all_years.json`.

4. **Multi-View Organization**:
   - `split_sociology_by_chapter.py`: Generate chapter-specific JSON files.
   - `split_sociology_by_type.py`: Generate type-specific JSON files (Objective, Short, Long).
   - `split_sociology_types_by_chapters.py`: Generate granular type-chapter matrices.

---

### 🚀 Phase 3: Pipeline Execution
> [!IMPORTANT]
> The following commands **MUST** be executed sequentially. Each script depends on the output of the previous one. An agent should request user permission for the entire sequence at once before starting.

```powershell
python batch_processing_sociology.py
python batch_annotate_sociology.py
python merge_sociology.py
python split_sociology_by_chapter.py
python split_sociology_by_type.py
python split_sociology_types_by_chapters.py
```

---

### 📝 Phase 4: Finalization
1. **Documentation**: Update `README.md` to document the new Sociology scripts.
2. **Version Control**: Stage and commit changes.

### ⚠️ Technical Guardrails
- **Maintain Consistency**: Follow the exactly same JSON structure and logging format as other subjects.
- **Reference Existing Code**: Treat `batch_processing_mathematics.py` and `batch_annotate_history.py` as primary templates.
