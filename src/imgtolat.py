import re
from pathlib import Path
from pix2text import Pix2Text
import logging
import onnxruntime
import warnings
# --- Suppress warnings and info logs ---
warnings.filterwarnings("ignore")
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Silence ONNXRuntime (0=verbose → 4=fatal)
onnxruntime.set_default_logger_severity(4)

# Silence Pix2Text, cnocr, cnstd, rapidocr loggers
for noisy_logger in ["pix2text", "cnocr", "cnstd", "rapidocr"]:
    logging.getLogger(noisy_logger).setLevel(logging.ERROR)

# Silence root and fastai/transformers-level logs
logging.getLogger().setLevel(logging.ERROR)
def convert_formula_images_in_md(md_path, output_path=None):
    """
    Convert formula images in Markdown file to LaTeX using Pix2Text.
    Handles redundant folder prefixes like 'temp/temp/formulas/...'.
    """
    md_path = Path(md_path).resolve()
    output_path = Path(output_path).resolve() if output_path else md_path

    p2t = Pix2Text(log_level='ERROR')

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'\$\$!\[Formula\]\(([^)]+\.(?:png|jpg|jpeg|gif|bmp))\)\$\$'

    def replace_formula(match):
        img_rel_path = match.group(1)
        img_path = Path(img_rel_path)

        # --- Auto-fix redundant "temp/temp" path case ---
        # If the Markdown file's parent folder name appears at the start of image path, drop it
        md_parent = md_path.parent.name
        parts = img_path.parts
        if len(parts) > 1 and parts[0].lower() == md_parent.lower():
            img_path = Path(*parts[1:])

        # Resolve full path correctly
        full_img_path = (md_path.parent / img_path).resolve()

        if not full_img_path.exists():
            print(f"Warning: Image not found - {full_img_path}")
            return match.group(0)

        try:
            latex_code = p2t.recognize(str(full_img_path), show_bar=False).strip()
            return latex_code or match.group(0)
        except Exception as e:
            print(f"Error converting {full_img_path.name}: {e}")
            return match.group(0)

    new_content = re.sub(pattern, replace_formula, content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # print(f"✅ Processed {md_path} → {output_path}")

# # Example usage
# if __name__ == "__main__":
#     # Convert formulas in 'input.md' and save to 'output.md'
#     convert_formula_images_in_md(r'preview-with-image-refs.md', 'NO-Lecture-2.md')
    
#     # To overwrite the original file, use:
#     # convert_formula_images_in_md('input.md')