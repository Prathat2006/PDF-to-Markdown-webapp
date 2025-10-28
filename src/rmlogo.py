from pathlib import Path
import re

def remove_logo_blocks(md_path: str):
    """
    Remove 'logo' lines and the image line immediately after each.
    """
    p = Path(md_path)
    text = p.read_text(encoding="utf-8")

    # Pattern:
    #   line with 'logo'
    #   optional blank line(s)
    #   an image line like ![...](...)
    pattern = r'(?mi)^logo\s*\n\s*!\[[^\]]*\]\([^)]+\)\s*\n?'

    cleaned = re.sub(pattern, '', text)

    # Optional: collapse 3+ newlines to 2
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    p.write_text(cleaned, encoding="utf-8")
    # print(f"Removed all 'logo' blocks from {p}")

def clean_caption_md_file(input_path: str, output_path: str = None):
    """
    Removes lines that only contain: 'other', 'bar chart', 'screenshot', or 'remote sensing'
    from a Markdown file.
    """
    banned = {"other", "bar chart", "screenshot", "remote sensing"}

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        stripped = line.strip().lower()
        # Keep line if it’s not one of the banned words
        if stripped not in banned:
            cleaned_lines.append(line)

    # If no output_path given, overwrite input file
    if output_path is None:
        output_path = input_path

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    # print(f"Cleaned file saved to: {output_path}")


# Example usage:
# clean_md_file("lecture7.md")

# Example usage:
# remove_logo_blocks("scratch\preview-with-image-refs.md")
