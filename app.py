from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import uuid
import json
from datetime import datetime
from main import full_converter, No_ai_converter
import subprocess
import os
import mimetypes
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="PDF → Markdown Converter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_ROOT = Path("temp_sessions")
TEMP_ROOT.mkdir(exist_ok=True)

HISTORY_FILE = Path("History/history.json")
HISTORY_FILE.parent.mkdir(exist_ok=True)

FRONTEND_BUILD_DIR = Path(__file__).parent / "Frontend" / "dist"

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------
@app.post("/convert", summary="Convert PDF to Markdown with image + formula analysis")
async def convert_pdf_to_md(file: UploadFile = File(...), ocr: bool = Form(False)):
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

        full_converter(str(input_pdf_path), str(output_md_path), bool(ocr))

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


@app.post("/convert_raw", summary="Convert PDF to Markdown without summarisation")
async def convert_pdf_to_md_raw(file: UploadFile = File(...), ocr: bool = Form(False)):
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

        No_ai_converter(str(input_pdf_path), str(output_md_path), bool(ocr))

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

        subprocess.run(
            ["pandoc", str(input_md_path), "-o", str(output_docx_path)],
            check=True,
        )

        if output_docx_path.exists():
            history = load_history()
            history_entry = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input_md": str(input_md_path),
                "output_docx": str(output_docx_path),
                "filename": file.filename,
                "type": "md_to_docx",
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


@app.get("/history", summary="Get conversion history")
def get_history():
    return JSONResponse(load_history())


@app.get("/get_file", summary="Fetch specific converted file (MD + PDF)")
def get_file(filename: str = Query(..., description="Original file name, e.g. 'SPASSIGN.pdf'")):
    history = load_history()
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
    if not pdf_file.is_absolute():
        pdf_file = Path.cwd() / pdf_file

    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found at {pdf_file}")

    return FileResponse(
        path=pdf_file,
        filename=pdf_file.name,
        media_type="application/pdf",
    )

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if os.path.exists(FRONTEND_BUILD_DIR):
    mimetypes.add_type("text/javascript", ".js")
    app.mount("/", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="frontend")

    log.info(f"Serving frontend from {FRONTEND_BUILD_DIR}")
else:
    log.warning(f"Frontend build directory not found at '{FRONTEND_BUILD_DIR}'. Serving API only.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9898)
