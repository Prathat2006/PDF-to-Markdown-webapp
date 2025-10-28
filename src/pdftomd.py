import logging
from collections.abc import Iterable
from pathlib import Path
import time
from docling_core.types.doc import DocItemLabel, DoclingDocument, NodeItem, TextItem, ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import InputFormat, ItemAndImageEnrichmentElement
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.base_model import BaseItemAndImageEnrichmentModel
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling_core.types.doc import PictureClassificationData


_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0

class ExampleFormulaUnderstandingPipelineOptions(PdfPipelineOptions):
    do_formula_understanding: bool = True
    generate_page_images: bool = True
    generate_picture_images: bool = True
    do_picture_classification: bool = True


class ExampleFormulaUnderstandingEnrichmentModel(BaseItemAndImageEnrichmentModel):
    images_scale = 2

    def __init__(self, enabled: bool, output_dir: Path):
        self.enabled = enabled
        self.output_dir = output_dir
        self.formula_dir = output_dir / "formulas"
        self.formula_dir.mkdir(parents=True, exist_ok=True)

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        return (
            self.enabled
            and isinstance(element, TextItem)
            and element.label == DocItemLabel.FORMULA
        )

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[ItemAndImageEnrichmentElement],
    ) -> Iterable[NodeItem]:
        if not self.enabled:
            return

        for idx, enrich_element in enumerate(element_batch):
            img = enrich_element.image
            img_path = self.formula_dir / f"formula_{idx+1}.png"
            img.save(img_path)
            enrich_element.item.text = f"![Formula]({img_path.as_posix()})"
            yield enrich_element.item

class CombinedPipeline(StandardPdfPipeline):
    output_dir: Path = Path("scratch")

    def __init__(self, pipeline_options: ExampleFormulaUnderstandingPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: ExampleFormulaUnderstandingPipelineOptions
        self.enrichment_pipe.append(ExampleFormulaUnderstandingEnrichmentModel(
           
                enabled=self.pipeline_options.do_formula_understanding,
                output_dir=self.output_dir,)
            )
        
        if self.pipeline_options.do_formula_understanding:
            self.keep_backend = True

    @classmethod
    def get_default_options(cls) -> ExampleFormulaUnderstandingPipelineOptions:
        return ExampleFormulaUnderstandingPipelineOptions()

def convert(input_doc_path: Path = None, output_dir: Path = None, OCR: bool = False) -> Path:
    logging.getLogger('docling').setLevel(logging.WARNING)
    logging.getLogger('docling_defaults').setLevel(logging.WARNING)
    # input_doc_path = Path(r"old\preview.pdf")
    # output_dir = Path("scratch")
    # input_doc_path = Path(r"old\preview.pdf")
    # output_dir = Path("scratch")
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_options = ExampleFormulaUnderstandingPipelineOptions()
    pipeline_options.do_formula_understanding = True
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.do_picture_classification = True
    pipeline_options.do_ocr = OCR
    # pipeline_options.do_picture_description =True
    CombinedPipeline.output_dir = output_dir

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=CombinedPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )

    start_time = time.time()
    conv_res = doc_converter.convert(input_doc_path)
    doc_filename = conv_res.input.file.stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    # Save images of figures and tables
    table_counter = 0
    picture_counters = {}  # Dynamic per-category counters
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = output_dir / f"{doc_filename}-table-{table_counter}.png"
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")
        if isinstance(element, PictureItem):
            # Extract top classification
            classification = 'other'
            for ann in element.annotations:
                if isinstance(ann, PictureClassificationData) and ann.predicted_classes:
                    classification = ann.predicted_classes[0].class_name
                    break
            if classification not in picture_counters:
                picture_counters[classification] = 0
            picture_counters[classification] += 1
            element_image_filename = output_dir / f"{doc_filename}-picture-{classification}-{picture_counters[classification]}.png"
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")
    # # Save Markdown with embedded images
    # md_filename_embedded = output_dir / f"{doc_filename}-with-images.md"
    # conv_res.document.save_as_markdown(md_filename_embedded, image_mode=ImageRefMode.EMBEDDED)

    # Save Markdown with referenced images
    md_filename_referenced = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename_referenced, image_mode=ImageRefMode.REFERENCED)

    end_time = time.time() - start_time
    _log.info(f"Document converted in {end_time:.2f} seconds.")
    # _log.info(f"Markdown saved at: {md_filename_embedded}, {md_filename_referenced}")
    # _log.info(f"Formula images saved in: {output_dir/'formulas'}")
    # _log.info(f"Page, table, and picture images saved in: {output_dir}")
    # output_path = md_filename_referenced
    return md_filename_referenced
# if __name__ == "__main__":
#     main()