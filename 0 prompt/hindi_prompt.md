# Project Brief: Hindi Data Pipeline Implementation

### 🎯 Objective
Implement a standardized data processing pipeline for Bihar Board Class 12 Hindi Previous Year Questions (2021-2026), ensuring 100% structural and functional parity with the existing History, Geography, and Mathematics pipelines.

---

### 🔍 Phase 1: Knowledge Discovery
1. **Syllabus Research**: Perform a targeted web search for the official **NCERT Class 12 Hindi syllabus** (Aroh and Vitan).
2. **Chapter Extraction**: Compile a clean list of chapter titles. This list will serve as the ground truth for AI-driven annotation in Phase 3.

---

### 🏗️ Phase 2: Script Implementation
> **Crucial Requirement**: The following scripts must mirror the logic, naming conventions, and directory structures of the existing subject scripts.

1. **Extraction** (`batch_processing_hindi.py`):
   - Scope: All PDFs in `hindi_papers/`.
   - Action: Utilize the existing `process_hindi_paper.py` utility which already supports granular types: `objective`, `essay`, `explanation`, `letter_writing`, `short_answer`, `long_answer`, `summary`, `translation`, and `comprehension`.

2. **Annotation** (`batch_annotate_hindi.py`):
   - Logic: Feed raw questions to Gemini (using `models/gemini-3-flash-preview`).
   - Task: Map each question to the NCERT chapters identified in Phase 1.
   - Output: Annotated JSON in `hindi_data_annotated/`.

3. **Consolidation** (`merge_hindi.py`):
   - Action: Merge yearly annotated files into a single master database: `hindi_pro/hindi_all_years.json`.

4. **Multi-View Organization**:
   - `split_hindi_by_chapter.py`: Generate chapter-specific JSON files.
   - `split_hindi_by_type.py`: Generate type-specific JSON files. **Mandatory Categories**:
     - `objective`: Vastunisth Prashna (MCQs).
     - `essay`: Nibandh.
     - `explanation`: Saprasang Vyakhya.
     - `letter_writing`: Patra Lekhan.
     - `short_answer`: Laghu Uttariya.
     - `long_answer`: Dirgha Uttariya.
     - `summary`: Saransh/Bhavarth.
     - `translation`: Anuvad.
     - `comprehension`: Gadyansh/Gadyansh based questions.
   - `split_hindi_types_by_chapters.py`: Generate granular type-chapter matrices.

---

### 🚀 Phase 3: Pipeline Execution
> [!IMPORTANT]
> The following commands **MUST** be executed sequentially. Each script depends on the output of the previous one. An agent should request user permission for the entire sequence at once before starting.

```powershell
python batch_processing_hindi.py
python batch_annotate_hindi.py
python merge_hindi.py
python split_hindi_by_chapter.py
python split_hindi_by_type.py
python split_hindi_types_by_chapters.py
```

---

### 📝 Phase 4: Finalization
1. **Documentation**: Update `README.md` to document the Hindi scripts.
2. **Version Control**: Stage and commit changes.

### ⚠️ Technical Guardrails
- **Maintain Consistency**: Follow the exactly same JSON structure and logging format as other subjects.
- **Reference Existing Code**: Treat `batch_processing_history.py` and `batch_annotate_history.py` as primary templates.
