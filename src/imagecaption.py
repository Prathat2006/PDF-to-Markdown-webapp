import os
import re
import mimetypes
import json
import time
import logging  # <-- Import the logging module
from PIL import Image
from google import genai
from google.genai import types
import google.api_core.exceptions
from dotenv import load_dotenv

# --- ADD THIS LINE ---
# Suppress INFO logs from all 'google' sub-loggers
logging.getLogger('google').setLevel(logging.WARNING)
load_dotenv()
# Configuration
MODEL_NAME = "gemini-2.5-flash-lite-preview-09-2025"
REQUESTS_BEFORE_PAUSE = 15
PAUSE_SECONDS = 30

def load_image_bytes(image_path: str):
    """Loads image file data and returns bytes + mime_type, or (None, None) on error."""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        # print(f"Loaded image bytes: {image_path}")
        return data, mime_type
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None, None
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None, None

def call_gemini_vision(client, image_bytes: bytes, mime_type: str, context_text: str):
    """
    Calls the Gemini API via SDK with the image and context to get a structured analysis.
    Implements exponential backoff for retry attempts.
    """

    system_instruction = (
        "You are an AI assistant analyzing technical documents. "
        "Your task is to evaluate an image based on the surrounding text context.\n\n"
        "Determine if the image is 'useful' or 'useless' and provide a brief reason.\n\n"
        "- 'useful' means: The image is a chart, graph, diagram, code snippet, "
        "architecture diagram, or a meaningful screenshot that supplements the text.\n"
        "- 'useless' means: The image is a generic logo, decorative shape, PowerPoint arrow, "
        "or placeholder image adding no informational value."
    )

    # Build message parts properly for SDK ≥0.6
    parts = [
        types.Part(text=system_instruction),
        types.Part(text=f"Here is the context from the document surrounding the image:\n---\n{context_text}\n---\nPlease analyze the following image:"),
        types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes))
    ]

    generation_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "is_useful": {"type": "BOOLEAN"},
                "reason": {"type": "STRING"}
            },
            "required": ["is_useful", "reason"]
        }
    )

    max_retries = 3
    delay = 1
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[parts],  # list-of-list is accepted
                config=generation_config
            )
            text = response.text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print(f"Invalid JSON from model:\n{text}")
                return {"is_useful": False, "reason": "Model returned invalid JSON"}
        except (google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded,
                google.api_core.exceptions.InternalServerError) as e:
            print(f"Transient API error ({attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return {"is_useful": False, "reason": f"API request failed after retries: {e}"}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"is_useful": False, "reason": str(e)}
    return {"is_useful": False, "reason": "All retries failed."}

def analyze_markdown_images(md_file_path: str):
    """
    Analyze images in a Markdown file using the Gemini Vision model.
    Loads API key from environment internally and initializes client automatically.
    """
    # Setup Gemini client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in environment variables.")
    client = genai.Client(api_key=api_key)

    # Read Markdown file
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file not found at {md_file_path}")
        return []
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return []

    results = []
    base_dir = os.path.dirname(md_file_path)
    image_regex = r'!\[.*?\]\((.*?)\)'
    image_matches = list(re.finditer(image_regex, md_content))
    total_images = len(image_matches)
    print(f"Found {total_images} total images to analyze.")

    request_count = 0

    for i, match in enumerate(image_matches):
        image_path = match.group(1)
        full_image_path = os.path.normpath(os.path.join(base_dir, image_path)) \
            if not os.path.isabs(image_path) else image_path

        # print(f"\n--- Analyzing image {i+1} of {total_images} ---")
        # print(f"Found image link: {image_path} -> {full_image_path}")

        context_start = max(0, match.start() - 500)
        context_end = min(len(md_content), match.end() + 500)
        context_text = md_content[context_start:context_end]

        img_bytes, mime_type = load_image_bytes(full_image_path)
        if img_bytes:
            # Rate limiting
            if request_count >= REQUESTS_BEFORE_PAUSE:
                print(f"Reached {REQUESTS_BEFORE_PAUSE} requests — pausing for {PAUSE_SECONDS} seconds...")
                time.sleep(PAUSE_SECONDS)
                request_count = 0

            analysis = call_gemini_vision(client, img_bytes, mime_type, context_text)
            request_count += 1

            results.append({
                "image_path": image_path,
                "full_path": full_image_path,
                "is_useful": analysis.get("is_useful", False),
                "reason": analysis.get("reason", "Analysis missing reason or failed.")
            })
        else:
            results.append({
                "image_path": image_path,
                "full_path": full_image_path,
                "is_useful": False,
                "reason": "Image file could not be loaded."
            })

    return results


# if __name__ == "__main__":
#     print("--- Markdown Image Analyzer ---")

#     # Setup the client
#     # If using Gemini Developer API (API key mode)
#     api_key = os.getenv("GOOGLE_API_KEY", None)
#     if not api_key:
#         print("Warning: GOOGLE_API_KEY is not set – replace with your key or set env var.")
#     client = genai.Client(api_key=api_key)
#     print("GenAI SDK client configured.")

#     md_path = r"scratch\NO-Lecture-2.md"
#     if not os.path.exists(md_path):
#         print(f"Error: File not found at {md_path}. Please check the path and try again.")
#     else:
#         analysis_results = analyze_markdown_images(md_path, client)
#         output_filename = "analysis_report.json"
#         try:
#             with open(output_filename, 'w', encoding='utf-8') as f:
#                 json.dump(analysis_results, f, indent=2, ensure_ascii=False)
#             print(f"\n--- Analysis Complete ---\nResults saved to {output_filename}")
#             print(json.dumps(analysis_results, indent=2))
#         except Exception as e:
#             print(f"\nError writing results to {output_filename}: {e}")
#             print("\n--- Raw Analysis Results (not saved) ---")
#             print(json.dumps(analysis_results, indent=2))
