import os
import re
import sys
import logging
from typing import List
from typing import Optional 
from llminit import LLMManager
# === Configuration ===
INPUT_PATH = r"final_output.md"
OUTPUT_PATH = r"final_output2.md"
ORDER_KEY = "default"


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


###########################
# Local (deterministic) cleaning utilities
###########################
def normalize_image_paths(md: str) -> str:
    def fix_path(p: str) -> str:
        return p.replace("\\", "/")

    md = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'![{m.group(1)}]({fix_path(m.group(2))})',
        md
    )

    md = re.sub(
        r'\[Image\]\(([^)]+)\)',
        lambda m: f'[Image]({fix_path(m.group(1))})',
        md
    )

    return md


def remove_placeholder_lines(md: str) -> str:
    lines = md.splitlines()
    keep = []
    placeholder_tokens = {'screenshot', 'other', 'bar chart', 'chart', 'image', 'temp\\temp', 'temp/temp'}
    for ln in lines:
        if ln.strip().lower() in placeholder_tokens:
            continue
        if re.fullmatch(r'\s*(screenshot|other|bar chart|chart)\s*', ln, flags=re.IGNORECASE):
            continue
        if len(ln.strip().split()) == 1 and ln.strip().lower() in {'other', 'screenshot'}:
            continue
        keep.append(ln)
    return "\n".join(keep)


def collapse_consecutive_duplicates(md: str) -> str:
    lines = md.splitlines()
    out = []
    prev = None
    for ln in lines:
        if ln.strip() == prev:
            continue
        out.append(ln)
        prev = ln.strip()
    return "\n".join(out)


def dedupe_adjacent_identical_sections(md: str) -> str:
    parts = re.split(r'(?m)^(#{1,6}\s.*)$', md)
    out_parts = []
    seen = set()
    i = 0
    while i < len(parts):
        if parts[i].strip() == "":
            out_parts.append(parts[i])
            i += 1
            continue
        heading = parts[i]
        content = parts[i + 1] if (i + 1) < len(parts) else ""
        key = heading.strip() + "::" + content.strip()[:200]
        if key in seen:
            i += 2
            continue
        seen.add(key)
        out_parts.append(heading)
        out_parts.append(content)
        i += 2
    return "".join(out_parts)


def preserve_math_blocks(md: str) -> tuple[str, dict]:
    token_map = {}

    def repl_display(m):
        token = f"__MATH_DISPLAY_{len(token_map)}__"
        token_map[token] = m.group(0)
        return token

    md = re.sub(r'\$\$.*?\$\$', repl_display, md, flags=re.DOTALL)

    def repl_inline(m):
        token = f"__MATH_INLINE_{len(token_map)}__"
        token_map[token] = m.group(0)
        return token

    md = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', repl_inline, md)
    return md, token_map


def restore_math_blocks(md: str, token_map: dict) -> str:
    for token, math in token_map.items():
        md = md.replace(token, math)
    return md


def local_clean(md_text: str) -> str:
    md_text = normalize_image_paths(md_text)
    md_text = remove_placeholder_lines(md_text)
    md_text = collapse_consecutive_duplicates(md_text)
    md_text = dedupe_adjacent_identical_sections(md_text)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    md_text = "\n".join([ln.rstrip() for ln in md_text.splitlines()])
    md_text = md_text.strip() + "\n"
    return md_text


###########################
# LLM orchestration
###########################
def prepare_llm_prompt(clean_md: str) -> str:
    system_instructions = (
        "You are a helpful assistant that rewrites raw lecture notes into clear, concise, "
        "and well-structured Markdown suitable for study/teaching. "
        "Be precise, preserve LaTeX math (do NOT modify content inside $$...$$ or $...$), "
        "preserve image links and file paths, and keep original section headings unless "
        "use proper space and punctuation. Aim for clarity and brevity; use new line and line break for sections and paragraphs."
        "a better heading improves clarity. Remove placeholder tokens like 'screenshot', 'other', "
        "or 'bar chart', but keep the intent (e.g., replace with `[bar chart]` or a short caption). "
        "Do not invent new equations or facts; clarify wording and remove duplicates."
        "while generating latex use $$ <latex> $$ for block math and $ <latex> $ for inline math. dont use \\[ \\] or \\( \\) for latex."
    )
    user_payload = (
        "Input markdown below. Produce rewritten markdown only — no extra commentary. "
        "Keep math and image links intact. Keep examples and list them with bolded labels. "
        "If a heading is duplicated, merge content. If an image is present, keep it with a short caption."
    )
    return f"{system_instructions}\n\n{user_payload}\n\n### BEGIN INPUT\n\n{clean_md}\n\n### END INPUT\n\n### OUTPUT:"


def call_llm_manager(clean_md: str, order_key: str = "default", timeout_seconds: int = 30) -> str:
    if LLMManager is None:
        raise RuntimeError("LLMManager module could not be imported. Skipping LLM step.")

    mgr = LLMManager()
    # logging.info("Setting up LLM instances from config...")
    llm_instances = mgr.setup_llm_with_fallback(fallback_order=None)
    if not llm_instances:
        raise RuntimeError("No LLMs available after setup.")

    prompt = prepare_llm_prompt(clean_md)
    # logging.info("Invoking LLM(s) in fallback order...")
    result = mgr.invoke_with_fallback(llm_instances, order_key, prompt)
    if not isinstance(result, str):
        raise ValueError("LLM returned unexpected non-string result.")
    return result


###########################
# Main logic
###########################
def rewrite_markdown_file(input_path: str, output_path: str, order_key: str = "default"):
    if not os.path.exists(input_path):
        logging.error("Input file not found: %s", input_path)
        sys.exit(2)

    with open(input_path, "r", encoding="utf-8") as f:
        raw_md = f.read()

    masked_md, token_map = preserve_math_blocks(raw_md)
    cleaned = local_clean(masked_md)
    cleaned = restore_math_blocks(cleaned, token_map)

    try:
        final_md = call_llm_manager(cleaned, order_key=order_key)
        if final_md and isinstance(final_md, str):
            logging.info("LLM returned rewritten markdown.")
        else:
            logging.warning("LLM returned empty or invalid output. Falling back to local clean.")
            final_md = cleaned
    except Exception as e:
        logging.warning("LLM rewrite failed or unavailable: %s", e)
        final_md = cleaned

    if not final_md.endswith("\n"):
        final_md += "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_md)

    logging.info("Wrote rewritten markdown to: %s", output_path)


# if __name__ == "__main__":
#     rewrite_markdown_file(INPUT_PATH, OUTPUT_PATH, ORDER_KEY)
