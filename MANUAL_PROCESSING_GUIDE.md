# Manual Hindi Question Paper Extraction Prompt

Use this prompt with Google AI Studio (https://aistudio.google.com/) or any Gemini API interface to manually process Hindi question papers.

---

## Instructions

1. Go to **Google AI Studio** (https://aistudio.google.com/)
2. Select **Gemini 2.0 Flash** or **Gemini 1.5 Pro** model
3. Upload the PDF file for the year you want to process
4. Copy and paste the prompt below
5. Click "Run"
6. Copy the JSON output and save it as `hindi_YYYY.json` (e.g., `hindi_2022.json`)

---

## THE PROMPT (Copy everything below)

```
Your task is to act as an expert data extraction engine. You will receive a PDF file of a Class 12 Hindi Question Paper. You must meticulously extract all questions and convert them into a single, clean JSON array.

Follow these instructions precisely:

1.  **JSON Structure**: The output must be a JSON array where each element is an object representing a single question.
2.  **Required Fields for All Questions**:
    - `id`: A unique string identifier. For each question type, numbering must start from 1. For example: "objective_1", "objective_2", ... "essay_1", "short_1", "long_1", etc. The numbering for each type must always start at 1, regardless of their order in the paper.
    - If two or more questions are given as alternatives (using "or"/"athva") under the same question number, represent them as `long_1_1`, `long_1_2`, etc. (or `short_5_1`, `short_5_2`, etc.) in the `id` field, where the main number is the question number and the sub-number distinguishes the alternatives.
    - `type`: The question type as a string. Use these exact keys:
        - `objective` (Vastunisth Prashna)
        - `essay` (Nibandh)
        - `explanation` (Saprasang Vyakhya)
        - `letter_writing` (Patra Lekhan)
        - `short_answer` (Laghu Uttariya)
        - `long_answer` (Dirgha Uttariya)
        - `summary` (Saransh/Bhavarth)
        - `translation` (Anuvad)
        - `comprehension` (Gadyansh/Sankshepan)
    - `question`: The full text of the question (in Hindi, as it appears).
    - `instructions`: Any specific instructions for this question (e.g., "Answer any 5", "Write in approx 250 words").

3.  **Fields for "objective" Type Questions**:
    - `options`: An object with keys "A", "B", "C", "D" containing the option text.
    - `answer`: The correct answer option key if marked or obvious (optional).

4.  **Fields for Questions (both "short_answer" and "long_answer") with Sub-Questions**:
    - If a question contains sub-questions, include:
        - `sub_questions`: An object containing the sub-questions associated with the main question.

5.  **Accuracy**: Ensure the text for questions, options, and sub-questions is extracted exactly as it appears in the document. Preserve all Hindi text accurately.

The PDF file is provided. Begin processing now and generate only the JSON array as your output.
```

---

## Failed Years to Process Manually

Process these years that failed in batch processing:

- **2022** (Safety filter block)
- **2021** (Safety filter block)
- **2020** (Timeout - 46 minutes)
- **2019** (Network error)
- **2017** (Safety filter block)
- **2012** (Safety filter block)

---

## After Processing

1. Save the JSON output to `hindi_data/hindi_YYYY.json`
2. Verify the JSON is valid using a JSON validator
3. Check that all questions are extracted correctly
4. Run the annotation script: `python batch_annotate_hindi.py`

---

## Example Output Format

```json
[
  {
    "id": "objective_1",
    "type": "objective",
    "question": "बिहार की राजधानी क्या है?",
    "instructions": "",
    "options": {
      "A": "पटना",
      "B": "दिल्ली",
      "C": "मुंबई",
      "D": "कोलकाता"
    }
  },
  {
    "id": "essay_1",
    "type": "essay",
    "question": "शिक्षा का महत्व पर निबंध लिखिए।",
    "instructions": "लगभग 250 शब्दों में लिखिए।"
  },
  {
    "id": "long_answer_1",
    "type": "long_answer",
    "question": "प्रेमचंद की कहानियों की विशेषताएं बताइए।",
    "instructions": ""
  }
]
```

---

## Tips for Manual Processing

1. **Use Gemini 1.5 Pro** if Flash blocks the content
2. **Try different safety settings** in AI Studio
3. **Split large PDFs** (like 2020) into smaller chunks if needed
4. **Review the PDF first** to check for quality issues
5. **Verify Hindi text** is preserved correctly in the output
