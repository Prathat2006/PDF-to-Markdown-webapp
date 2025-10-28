from pathlib import Path
from src.pdftomd import convert
from src.rmlogo import remove_logo_blocks ,clean_caption_md_file
from src.imgtolat import convert_formula_images_in_md
from src.imagecaption import analyze_markdown_images
from src.rmuselessimage import clean_markdown
from src.notesconverter import rewrite_markdown_file


def full_converter(input_pdf:str , output_md:str, ocr: bool = False):

    input_path = Path(input_pdf)
    output_dir = Path("temp")
    output=convert(input_path, output_dir,ocr)

    # md_file = output_dir / f"{input_path.stem}-with-images.md"
    remove_logo_blocks(output)

    convert_formula_images_in_md(str(output))

    analysis_results = analyze_markdown_images(str(output))
    json_report_path = output_dir / "analysis_report.json"
    with open(json_report_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(analysis_results, f, indent=2)

    cleaned_md_path = Path(output_md)
    clean_markdown(output, json_report_path, cleaned_md_path)
    rewrite_markdown_file(str(cleaned_md_path), str(cleaned_md_path), order_key="default")


def No_ai_converter(input_pdf:str , output_md:str, ocr: bool = False):

    input_path = Path(input_pdf)
    output_dir = Path("temp")
    output=convert(input_path, output_dir,ocr)

    # md_file = output_dir / f"{input_path.stem}-with-images.md"
    remove_logo_blocks(output)

    convert_formula_images_in_md(str(output))

    analysis_results = analyze_markdown_images(str(output))
    json_report_path = output_dir / "analysis_report.json"
    with open(json_report_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(analysis_results, f, indent=2)

    # Step 5: Clean the markdown file based on JSON report
    cleaned_md_path = Path(output_md)
    clean_markdown(output, json_report_path, cleaned_md_path)

    # Step 6: Clean captions from the markdown file (fix here)
    clean_caption_md_file(cleaned_md_path)

    # rewrite_markdown_file(str(cleaned_md_path), str(cleaned_md_path), order_key="default")
# full_converter(r"old\preview.pdf", r"final_output.md")