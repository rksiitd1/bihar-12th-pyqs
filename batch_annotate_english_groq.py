import os
import json
import pathlib
import textwrap
import re
import time
from dotenv import load_dotenv
from groq import Groq

def clean_json_response(raw_text: str) -> str:
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

ENGLISH_CHAPTERS = [
    # Flamingo (Prose)
    "The Last Lesson",
    "Lost Spring",
    "Deep Water",
    "The Rattrap",
    "Indigo",
    "Poets and Pancakes",
    "The Interview",
    "Going Places",

    # Flamingo (Poetry)
    "My Mother at Sixty-Six",
    "Keeping Quiet",
    "A Thing of Beauty",
    "A Roadside Stand",
    "Aunt Jennifer's Tigers",

    # Vistas
    "The Third Level",
    "The Tiger King",
    "Journey to the End of the Earth",
    "The Enemy",
    "On the Face of It",
    "Memories of Childhood"
]

def generate_english_annotation_prompt(chapters, questions):
    chapter_lines = [f"{ch}" for ch in chapters]
    prompt = textwrap.dedent(f"""
    You are an expert in educational content classification.
    You will receive a JSON array of questions from a Bihar Board Class 12 English question paper.
    Your task is to annotate each question with the correct chapter name from the official NCERT Class 12 English chapters below.
    - Insert the field "chapter_name": "<name>" immediately after the "type" field in each question object.
    - Only use the exact chapter names from the list below.
    - If a question does not belong to any specific chapter (e.g., Grammar, Unseen Passage, Essay, Letter), set "chapter_name" to "General".
    - Output the result as a JSON array, with the new fields added to each question.

    Chapters:
    {chr(10).join(chapter_lines)}

    Here is the input JSON array of questions:
    ```json
    {json.dumps(questions, ensure_ascii=False, indent=2)}
    ```

    Output only the annotated JSON array.
    """)
    return prompt

def main():
    print("Batch English Question Annotator (Groq)")
    print("="*40)
    
    load_dotenv()
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in environment variables.")
        return

    client = Groq(api_key=GROQ_API_KEY)

    data_folder = pathlib.Path("english_data")
    out_folder = pathlib.Path("english_data_annotated")
    out_folder.mkdir(exist_ok=True)
    
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in english_data/!")
        return
        
    chapters = ENGLISH_CHAPTERS
    
    for fpath in files:
        # Filter for 2021-2026 if needed
        try:
            year_str = fpath.stem.split('_')[-1]
            year = int(year_str)
            if not (2021 <= year <= 2026):
                continue
        except ValueError:
            pass 

        out_path = out_folder / fpath.name
        if out_path.exists():
            print(f"⏭️  Skipping {fpath.name} (already annotated)")
            continue
            
        print(f"\nProcessing: {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        # Split into chunks to avoid rate limits (10k TPM limit)
        CHUNK_SIZE = 10  # Process 10 questions at a time
        total_chunks = (len(questions) + CHUNK_SIZE - 1) // CHUNK_SIZE
        
        print(f"Total questions: {len(questions)}, splitting into {total_chunks} chunks")
        
        all_annotated = []
        
        for chunk_idx in range(total_chunks):
            start_idx = chunk_idx * CHUNK_SIZE
            end_idx = min(start_idx + CHUNK_SIZE, len(questions))
            chunk_questions = questions[start_idx:end_idx]
            
            print(f"\n[Chunk {chunk_idx + 1}/{total_chunks}] Processing questions {start_idx + 1}-{end_idx}")
            
            prompt = generate_english_annotation_prompt(chapters, chunk_questions)
            
            max_retries = 3
            retry_delay = 5
            
            annotated_chunk = None
            
            for attempt in range(max_retries):
                try:
                    print("Sending to Groq (Moonshot Kimi)...")
                    
                    completion = client.chat.completions.create(
                        model="moonshotai/kimi-k2-instruct-0905",
                        messages=[
                          {
                            "role": "user",
                            "content": prompt
                          }
                        ],
                        temperature=1.0,
                        max_tokens=16384,  # Maximum allowed by this model 
                        top_p=1,
                        stream=True,
                        stop=None
                    )

                    full_response = ""
                    for chunk in completion:
                        content = chunk.choices[0].delta.content or ""
                        full_response += content
                        print(content, end="", flush=True)
                    print()
                    
                    print("Response received. Parsing...")
                    cleaned_json_string = clean_json_response(full_response)
                    annotated_chunk = json.loads(cleaned_json_string)
                    break # Success
                    
                except Exception as e:
                    print(f"\nError: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print(f"Failed after retries.")
            
            if annotated_chunk:
                all_annotated.extend(annotated_chunk)
                print(f"✓ Chunk {chunk_idx + 1} processed successfully")
                # Add delay between chunks to respect rate limits
                if chunk_idx < total_chunks - 1:
                    print("Waiting 10 seconds before next chunk...")
                    time.sleep(10)
            else:
                print(f"⚠️ Skipping {fpath.name} due to errors")
                all_annotated = None
                break
        
        if all_annotated and len(all_annotated) == len(questions):
            print(f"\n✅ Successfully processed all {len(all_annotated)} questions")
            # Reorder fields
            for i, q in enumerate(all_annotated):
                if "type" in q and "chapter_name" in q:
                    new_q = {}
                    for k, v in q.items():
                        new_q[k] = v
                        if k == "type":
                            new_q["chapter_name"] = q["chapter_name"]
                    all_annotated[i] = new_q
            
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(all_annotated, f, indent=4, ensure_ascii=False)
            print(f"✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    main()
