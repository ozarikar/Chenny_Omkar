"""
Part 1 — Structured Extraction

This script converts unstructured course text (e.g., “CSC 170 Programming and
Problem Solving 4 a T. Allen 1:50–3:50PM -M-W-F- OLIN 208”) into structured,
validated rows using a Pydantic model defined in schema.py.

In Part 1, your task is to:

- Write code in `extract_structured_record()` that uses your local LLM
  (through Ollama) to extract structured data following the schema.

- Pass SectionRow.model_json_schema() as the `format` argument when calling
  the model so it returns a valid JSON object.

- Parse the model output, validate it with SectionRow(**data), and return
  the resulting object.

For now, the provided stub runs end-to-end with a placeholder that returns
blank fields. This allows you to test the pipeline and see how the validation
and scoring work before adding your model logic.
"""

import csv
from pydantic import ValidationError
from schema import SectionRow
from ollama import chat


def extract_structured_record(line: str) -> SectionRow:
    """
    Use an LLM to extract structured data for one course listing.

    TODO:
      - Write a prompt that tells the model what to extract.
      - Call your chosen Ollama model (e.g., gemma3:4b, granite3:2b, etc.).
      - Pass SectionRow.model_json_schema() so the model knows the expected format.
      - Parse the model's JSON response.
      - Validate the result with SectionRow(**data).
    """
    # Create a prompt that explains what we want to extract
    prompt = f"""Extract all structured course information from the given text line. 
Always return output strictly as a single JSON object following the exact schema below — no extra text or commentary.

Input text:
{line}

Schema and rules:
{{
  "program": string,                # Exactly 3 uppercase letters (e.g., CSC, MAT, ECO). If not found, return null.
  "number": string,                 # 3 digits optionally followed by 'L' (e.g., 210, 210L). If not found, return null.
  "section": string or null,        # Single lowercase letter (e.g., 'a') or null if missing.
  "title": string or null,          # Full course title.
  "credits": float or null,         # e.g., 3.0, 4.0. Must be numeric.
  "days": string or null,           # Pattern like '-M-W-F-' or '--T-R--'. Return null if it shows '-------'.
  "times": string or null,          # e.g., '9:00-9:50AM'. Return null if 'TBA'.
  "faculty": string or null,        # Instructor’s full name.
  "room": string or null,           # Format 'BUILDING ROOM' (e.g., 'OLIN 208'). Return null if 'TBA'.
  "tags": string or null            # Optional classification codes separated by commas, e.g., 'E1,A'. Null if none.
}}

Important rules:
- Always return JSON with double quotes around property names and string values.
- Never include explanations or comments in output.
- If something is missing or unclear, set the value to null rather than omitting the key.
- Preserve capitalization and punctuation in text fields like 'title' and 'faculty'.
- Do not guess field values; derive them only from the input text.

Example Input:
"CSC 210L a Intro to Data Science 4.0 -M-W-F- 10:00-10:50AM Smith, John OLIN 208 E1,A"

Example Output:
{{
  "program": "CSC",
  "number": "210L",
  "section": "a",
  "title": "Intro to Data Science",
  "credits": 4.0,
  "days": "-M-W-F-",
  "times": "10:00-10:50AM",
  "faculty": "Smith, John",
  "room": "OLIN 208",
  "tags": "E1,A"
}}
"""

    try:
        # Call Ollama model
        response = chat(
            model='granite3.2:2b',  # You can change this to other models like gemma3:4b
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0},
            format=SectionRow.model_json_schema()
        )
        
        # Parse and validate the response
        data = response.message.content
        return SectionRow.model_validate_json(data)
        
    except Exception as e:
        print(f"Error during Ollama chat call: {e}")
        raise


def process_file(in_path: str, out_path: str):
    """
    Read unstructured text from in_path, extract structured data for each line,
    and write results to out_path as a semicolon-delimited CSV.
    """
    with open(in_path, encoding="utf-8") as fin, open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter=";")

        # Write CSV header based on schema fields
        writer.writerow(SectionRow.model_fields.keys())

        count = 0
        limit = 5
        print(limit) # set a small limit for debugging; change to -1 for no limit ...

        for line in fin:
            if not line.strip():
                continue
            #if count >= limit:  # or you could just remove these two lines for no limit
            #    break
            try:
                record = extract_structured_record(line)
                print(f"Processed line {count + 1}: {record}")
                # Optional: view the validated record for debugging
                # print(record.model_dump_json(indent=2))

                writer.writerow(record.model_dump().values())

            except ValidationError as e:
                print("Validation test failed — skipping this line.")
                print(f"  Input: {line.strip()}")
                for err in e.errors():
                    loc = ".".join(str(x) for x in err["loc"])
                    msg = err["msg"]
                    val = err.get("input_value", "")
                    print(f"    Field: {loc} | Problem: {msg} | Value: {val}")

            except Exception as e:
                print(f"Unexpected error — skipping line: {line.strip()}")
                print(f"  {type(e).__name__}: {e}")

            count += 1


if __name__ == "__main__":
    # Process training data (Part 1)
    process_file("raw/testing.txt", "out/sections_train.csv")

    # Later, after refinement, uncomment to process the test set (Part 2)
    # process_file("raw/testing.txt", "out/sections_test.csv")
