
import json
import re
from pathlib import Path

from pypdf import PdfReader
from app.models import Record


PDF_PATH = Path("data/raw/constitution.pdf")
OUTPUT_PATH = Path("data/records.json")


def join_wrapped_lines(text):
    """
    Join PDF lines that are wrapped across multiple lines.
    Preserve paragraph boundaries.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return " ".join(cleaned_lines)


def get_part(article_no):
    """Identify the Constitution Part using article number ranges."""
    try:
        number = int(re.match(r"\d+", article_no).group())
    except (AttributeError, ValueError):
        return "Not identified"

    if number <= 4:
        return "Part I"
    elif number <= 11:
        return "Part II"
    elif number <= 35:
        return "Part III"
    elif number <= 51:
        return "Part IV"
    elif article_no == "51A":
        return "Part IVA"
    elif number <= 151:
        return "Part V"
    elif number <= 237:
        return "Part VI"
    elif number <= 242:
        return "Part VIII"
    elif number <= 243:
        return "Part IX"
    elif number <= 243:
        return "Part IX"
    elif number <= 244:
        return "Part X"
    elif number <= 263:
        return "Part XI"
    elif number <= 300:
        return "Part XII"
    elif number <= 307:
        return "Part XIII"
    elif number <= 323:
        return "Part XIV"
    elif number <= 323:
        return "Part XIV"
    elif number <= 329:
        return "Part XV"
    elif number <= 342:
        return "Part XVI"
    elif number <= 351:
        return "Part XVII"
    elif number <= 360:
        return "Part XVIII"
    elif number <= 367:
        return "Part XIX"
    elif number == 368:
        return "Part XX"
    else:
        return "Part XXI / XXII"


def extract_pdf_text():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))

    print("Total PDF pages:", len(reader.pages))

    page_texts = []

    for page_number, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""

        # Join wrapped lines BEFORE article extraction
        cleaned_text = join_wrapped_lines(raw_text)

        if cleaned_text:
            page_texts.append({
                "page": page_number,
                "text": cleaned_text
            })

    return page_texts


def parse_articles(page_texts):
    """
    Identify article headings and extract their titles and text.
    """

    full_text = ""
    page_ranges = []

    for item in page_texts:
        start = len(full_text)
        full_text += item["text"] + " "
        end = len(full_text)

        page_ranges.append({
            "start": start,
            "end": end,
            "page": item["page"]
        })

    # Article headings generally contain a number, title and em dash.
    article_pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"(\d{1,3}[A-Z]?)\.\s+"
        r"([A-Z][^—–]{2,180}?)"
        r"\s*\.?\s*[—–]"
    )

    matches = list(article_pattern.finditer(full_text))

    if not matches:
        raise ValueError(
            "No article headings found. Check the PDF format and heading pattern."
        )

    records = []

    for index, match in enumerate(matches):
        article_no = match.group(1).strip()
        title = match.group(2).strip().rstrip(" .")

        content_start = match.end()

        if index + 1 < len(matches):
            content_end = matches[index + 1].start()
        else:
            content_end = len(full_text)

        article_text = full_text[content_start:content_end].strip()

        # Find the PDF page containing this article heading
        source_page = 0

        for page_range in page_ranges:
            if page_range["start"] <= match.start() < page_range["end"]:
                source_page = page_range["page"]
                break

        if not title or not article_text:
            continue

        record = Record(
            article_no=article_no,
            title=title,
            part=get_part(article_no),
            text=article_text,
            amended_by=[],
            source_page=source_page
        )

        records.append(record)

    return records


def save_records(records):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = [
        {
            "article_no": record.article_no,
            "title": record.title,
            "part": record.part,
            "text": record.text,
            "amended_by": record.amended_by,
            "source_page": record.source_page
        }
        for record in records
    ]

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print("\nRecords saved successfully!")
    print("Output file:", OUTPUT_PATH)
    print("Total article records:", len(records))


def main():
    print("Starting SamvidhanSathi PDF ingestion...")

    page_texts = extract_pdf_text()

    print("Cleaning and joining wrapped lines...")

    records = parse_articles(page_texts)

    save_records(records)

    print("\nFirst 3 extracted articles:")

    for record in records[:3]:
        print("\nArticle:", record.article_no)
        print("Title:", record.title)
        print("Text:", record.text[:250])
        print("Source page:", record.source_page)


if __name__ == "__main__":
    main()
