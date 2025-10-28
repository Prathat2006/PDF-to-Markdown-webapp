import json
import re
from pathlib import Path

def clean_markdown(md_path: Path, json_path: Path, output_path: Path):
    # Load JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build lookup dicts
    useful_lookup = {}
    fullpath_lookup = {}
    for entry in data:
        normalized = entry["image_path"].replace("/", "\\")
        useful_lookup[normalized] = entry["is_useful"]
        fullpath_lookup[normalized] = entry["full_path"]

    # Read Markdown content
    md_text = md_path.read_text(encoding="utf-8")

    # Regex pattern to match Markdown image syntax: ![Alt](path)
    image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

    # Replace function
    def replace_image(match):
        alt_text = match.group(1)
        img_path = match.group(2).strip()
        normalized = img_path.replace("/", "\\")
        is_useful = useful_lookup.get(normalized, True)  # Default True if not found

        if not is_useful:
            # print(f"🗑️ Removing non-useful image: {img_path}")
            return ""  # Remove it entirely

        # Replace with full path if useful
        full_path = fullpath_lookup.get(normalized, img_path)
        # if full_path != img_path:
        #     # print(f"🔁 Updating useful image path:\n  from: {img_path}\n  to:   {full_path}")
        # else:
        #     # print(f"✅ Keeping useful image (path unchanged): {img_path}")

        return f"![{alt_text}]({full_path})"

    # Apply replacements
    cleaned_md = re.sub(image_pattern, replace_image, md_text)

    # Clean up excess blank lines
    cleaned_md = re.sub(r'\n{3,}', '\n\n', cleaned_md).strip()

    # Write output
    output_path.write_text(cleaned_md, encoding="utf-8")
    # print(f"\n✅ Cleaned Markdown saved to: {output_path}")


# Example usage
# if __name__ == "__main__":
#     md_file = Path(r"scratch\NO-Lecture-2.md")
#     json_file = Path(r"analysis_report.json")
#     output_file = Path("output_cleaned.md")
#     clean_markdown(md_file, json_file, output_file)
