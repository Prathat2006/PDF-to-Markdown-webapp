from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid
import json
from datetime import datetime
from main import full_converter ,No_ai_converter
import subprocess

app = FastAPI(title="PDF → Markdown Converter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root folder for temporary sessions
TEMP_ROOT = Path("temp_sessions")
TEMP_ROOT.mkdir(exist_ok=True)

HISTORY_FILE = Path("History/history.json")


def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


@app.post("/convert", summary="Convert PDF to Markdown with image + formula analysis")
async def convert_pdf_to_md(
    file: UploadFile = File(...),
    ocr: bool = Form(False)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    session_id = uuid.uuid4().hex
    temp_dir = TEMP_ROOT / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    input_pdf_path = temp_dir / file.filename
    output_md_path = temp_dir / f"{Path(file.filename).stem}.md"

    try:
        with open(input_pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run pipeline
        full_converter(str(input_pdf_path), str(output_md_path), bool(ocr))

        # If successful, append to history
        if output_md_path.exists():
            history = load_history()
            history_entry = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input_pdf": str(input_pdf_path),
                "output_md": str(output_md_path),
                "filename": file.filename,
                "ocr": bool(ocr),
            }
            history.append(history_entry)
            save_history(history)

            return FileResponse(
                path=output_md_path,
                filename=output_md_path.name,
                media_type="text/markdown",
            )
        else:
            raise HTTPException(status_code=500, detail="Markdown output not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    finally:
        file.file.close()

@app.post("/convert_raw", summary="Convert PDF to Markdown with image + formula analysis_without summarise")
async def convert_pdf_to_md_raw(
    file: UploadFile = File(...),
    ocr: bool = Form(False)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    session_id = uuid.uuid4().hex
    temp_dir = TEMP_ROOT / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    input_pdf_path = temp_dir / file.filename
    output_md_path = temp_dir / f"{Path(file.filename).stem}.md"

    try:
        with open(input_pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run pipeline
        No_ai_converter(str(input_pdf_path), str(output_md_path), bool(ocr))

        # If successful, append to history
        if output_md_path.exists():
            history = load_history()
            history_entry = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input_pdf": str(input_pdf_path),
                "output_md": str(output_md_path),
                "filename": file.filename,
                "ocr": bool(ocr),
            }
            history.append(history_entry)
            save_history(history)

            return FileResponse(
                path=output_md_path,
                filename=output_md_path.name,
                media_type="text/markdown",
            )
        else:
            raise HTTPException(status_code=500, detail="Markdown output not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    finally:
        file.file.close()


@app.post("/convert_md_to_docx", summary="Convert Markdown to DOCX")
async def convert_md_to_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".md"):
        raise HTTPException(status_code=400, detail="Only Markdown files are supported.")

    session_id = uuid.uuid4().hex
    temp_dir = TEMP_ROOT / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    input_md_path = temp_dir / file.filename
    output_docx_path = temp_dir / f"{Path(file.filename).stem}.docx"

    try:
        with open(input_md_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        subprocess.run([
            "pandoc",
            str(input_md_path),
            "-o",
            str(output_docx_path)
        ], check=True)

        if output_docx_path.exists():
            # Append to history as well
            history = load_history()
            history_entry = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input_md": str(input_md_path),
                "output_docx": str(output_docx_path),
                "filename": file.filename,
                "type": "md_to_docx"
            }
            history.append(history_entry)
            save_history(history)

            return FileResponse(
                path=output_docx_path,
                filename=output_docx_path.name,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            raise HTTPException(status_code=500, detail="DOCX output not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    finally:
        file.file.close()


@app.get("/", summary="Health Check")
def root():
    return JSONResponse({"message": "PDF → Markdown Converter API is running."})


@app.get("/history", summary="Get conversion history")
def get_history():
    """
    Returns all previously converted files (PDF → MD or MD → DOCX)
    from the shared history.json file.
    """
    history = load_history()
    return JSONResponse(history)

@app.get("/get_file", summary="Fetch specific converted file (MD + PDF)")
def get_file(filename: str = Query(..., description="Original file name, e.g. 'SPASSIGN.pdf'")):
    """
    Returns both Markdown and PDF file paths (or their content) for a specific file name
    by looking it up in the shared history.json.
    """

    history = load_history()

    # Find matching record by filename (case-insensitive)
    entry = next((item for item in history if item["filename"].lower() == filename.lower()), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"No record found for {filename}")

    md_path = entry.get("output_md")
    pdf_path = entry.get("input_pdf")

    if not md_path or not pdf_path:
        raise HTTPException(status_code=500, detail="Missing Markdown or PDF path in record.")

    md_file = Path(md_path)
    pdf_file = Path(pdf_path)

    if not (md_file.exists() and pdf_file.exists()):
        raise HTTPException(status_code=404, detail="One or both files are missing on disk.")

    # Option 1: Return file paths (for frontend fetch)
    # return JSONResponse({
    #     "markdown_path": str(md_file),
    #     "pdf_path": str(pdf_file)
    # })

    # Option 2: Return actual file contents (for immediate preview)
    with open(md_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    return JSONResponse({
        "filename": filename,
        "markdown_content": markdown_content,
        "pdf_url": f"/download_pdf?path={pdf_path}"
    })

@app.get("/download_pdf", summary="Serve a PDF file directly")
def download_pdf(path: str = Query(..., description="Full path to PDF file")):
    pdf_file = Path(path)

    # If relative path → make it absolute
    if not pdf_file.is_absolute():
        pdf_file = Path.cwd() / pdf_file

    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found at {pdf_file}")

    return FileResponse(
        path=pdf_file,
        filename=pdf_file.name,
        media_type="application/pdf"
    )
