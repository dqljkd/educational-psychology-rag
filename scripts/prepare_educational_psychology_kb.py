from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, List

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_sources"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "data" / "reports"


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def copy_raw_sources(paths: Iterable[Path]) -> List[Path]:
    copied: List[Path] = []
    for path in paths:
        destination = RAW_DIR / path.name
        if path.resolve() != destination.resolve():
            shutil.copy2(path, destination)
        copied.append(destination)
    return copied


def parse_structured_txt(path: Path) -> List[Dict[str, object]]:
    text = normalize_text(path.read_text(encoding="utf-8"))
    chunks_section = re.search(
        r"=+\s*03_CHUNKS_FOR_RAG\s*=+\s*(.*?)\s*=+\s*04_QA_TEST_SET\s*=+",
        text,
        flags=re.S,
    )
    if not chunks_section:
        raise ValueError("Could not find 03_CHUNKS_FOR_RAG section.")

    records: List[Dict[str, object]] = []
    blocks = [block.strip() for block in chunks_section.group(1).split("--------------------------------------------------") if block.strip()]
    for block in blocks:
        item = {}
        content_match = re.search(r"\[CONTENT\]\n(.*)", block, flags=re.S)
        content = normalize_text(content_match.group(1)) if content_match else ""
        for key in [
            "ID",
            "CATEGORY",
            "TOPIC",
            "KEYWORDS",
            "AUDIENCE",
            "RISK_LEVEL",
            "SOURCE_ID",
            "SOURCE_TITLE",
            "SOURCE_YEAR",
            "SOURCE_URL",
        ]:
            match = re.search(rf"\[{key}\]\s*(.+)", block)
            item[key.lower()] = match.group(1).strip() if match else ""

        record = {
            "id": item["id"],
            "source": path.name,
            "source_type": "structured_txt",
            "category": item["category"],
            "topic": item["topic"],
            "keywords": [part.strip() for part in item["keywords"].split("，") if part.strip()],
            "audience": item["audience"],
            "risk_level": item["risk_level"],
            "source_id": item["source_id"],
            "source_title": item["source_title"],
            "source_year": item["source_year"],
            "source_url": item["source_url"],
            "chunk_index": len(records),
            "content": content,
        }
        records.append(record)
    return records


def infer_pdf_category(file_name: str) -> str:
    if "教师教学手册" in file_name or "1389703959379" in file_name:
        return "教师教学与课堂支持"
    if "教育心理学" in file_name or "094197-01" in file_name:
        return "教育心理学教材"
    if "普通心理学" in file_name:
        return "普通心理学教材"
    return "原始文献"


def infer_risk_level(text: str) -> str:
    high_risk_terms = ["自伤", "自杀", "危机", "暴力", "严重抑郁", "拒学"]
    if any(term in text for term in high_risk_terms):
        return "高风险需转介"
    return "普通支持"


def build_pdf_records(path: Path, max_pages: int | None = None) -> List[Dict[str, object]]:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    reader = PdfReader(str(path))
    records: List[Dict[str, object]] = []
    pages = reader.pages[:max_pages] if max_pages else reader.pages

    for index, page in enumerate(pages):
        text = normalize_text(page.extract_text() or "")
        if len(text) < 120:
            continue

        title = f"{path.stem} 第{index + 1}页"
        records.append(
            {
                "id": f"{path.stem}-p{index + 1:04d}",
                "source": path.name,
                "source_type": "pdf_page",
                "category": infer_pdf_category(path.name),
                "topic": title,
                "keywords": [],
                "audience": "教师/学生/家长/学校心理支持团队",
                "risk_level": infer_risk_level(text),
                "source_id": "",
                "source_title": path.stem,
                "source_year": "",
                "source_url": "",
                "chunk_index": index,
                "content": text,
            }
        )
    return records


def write_jsonl(path: Path, records: List[Dict[str, object]]) -> None:
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_report(path: Path, report: Dict[str, object]) -> None:
    markdown = [
        "# 清洗报告",
        "",
        f"- 生成时间：{report['generated_at']}",
        f"- 原始文件数：{report['source_files']}",
        f"- 结构化记录数：{report['structured_records']}",
        f"- PDF页级记录数：{report['pdf_records']}",
        f"- 总记录数：{report['total_records']}",
        "",
        "## 文件明细",
    ]
    for item in report["details"]:
        markdown.append(f"- `{item['file']}`: {item['records']} 条")
    path.write_text("\n".join(markdown) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare educational psychology knowledge base data.")
    parser.add_argument("--structured-txt", required=True, help="Path to the structured TXT knowledge package.")
    parser.add_argument("--pdf", action="append", default=[], help="Path to a PDF source. Can be repeated.")
    parser.add_argument("--max-pages", type=int, default=40, help="Maximum pages to extract per PDF.")
    args = parser.parse_args()

    ensure_dirs()

    txt_path = Path(args.structured_txt).expanduser().resolve()
    pdf_paths = [Path(item).expanduser().resolve() for item in args.pdf]
    copied_sources = copy_raw_sources([txt_path, *pdf_paths])

    structured_records = parse_structured_txt(RAW_DIR / txt_path.name)
    structured_path = PROCESSED_DIR / "educational_psychology_structured_chunks.jsonl"
    write_jsonl(structured_path, structured_records)

    pdf_records: List[Dict[str, object]] = []
    details = [{"file": structured_path.name, "records": len(structured_records)}]
    for pdf_path in pdf_paths:
        cleaned = build_pdf_records(RAW_DIR / pdf_path.name, max_pages=args.max_pages)
        output_path = PROCESSED_DIR / f"{pdf_path.stem}_pages.jsonl"
        write_jsonl(output_path, cleaned)
        pdf_records.extend(cleaned)
        details.append({"file": output_path.name, "records": len(cleaned)})

    manifest = {
        "structured_jsonl": structured_path.name,
        "pdf_jsonl_files": [f"{pdf.stem}_pages.jsonl" for pdf in pdf_paths],
        "raw_sources": [path.name for path in copied_sources],
    }
    (PROCESSED_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = {
        "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "source_files": len(copied_sources),
        "structured_records": len(structured_records),
        "pdf_records": len(pdf_records),
        "total_records": len(structured_records) + len(pdf_records),
        "details": details,
    }
    write_report(REPORT_DIR / "cleaning_report.md", report)


if __name__ == "__main__":
    main()
