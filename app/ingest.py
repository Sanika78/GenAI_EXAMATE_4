
import json
import re
from pathlib import Path

from pypdf import PdfReader
from app.models import Record

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data" / "raw" / "constitution.pdf"
OUTPUT_PATH = BASE_DIR / "data" / "records.json"


# Match headings such as:
# 21. Protection of life and personal liberty.—
ARTICLE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?P<number>\d{1,3}[A-Z]?)\.\s+"
    r"(?P<title>[A-Z][^—–]{2,180}?)"
    r"\s*(?:\.\s*)?[—–]"
)


def join_wrapped_lines(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " ".join(lines)


def get_part(article_no):
    match = re.fullmatch(r"(\d+)([A-Z]?)", str(article_no).upper())

    if not match:
        return "Not identified"

    number = int(match.group(1))
    suffix = match.group(2)

    if number <= 4:
        return "Part I"
    if number <= 11:
        return "Part II"
    if number <= 35:
        return "Part III"
    if number == 51 and suffix == "A":
        return "Part IVA"
    if 36 <= number <= 51:
        return "Part IV"
    if 52 <= number <= 151:
        return "Part V"
    if 152 <= number <= 237:
        return "Part VI"
    if 239 <= number <= 242:
        return "Part VIII"
    if number == 243 and suffix == "":
        return "Part IX"
    if number == 243 and suffix in "PQRSTUVWXY":
        return "Part IXA"
    if number == 243 and suffix == "Z":
        return "Part IXB"
    if number == 244:
        return "Part X"
    if 245 <= number <= 263:
        return "Part XI"
    if 264 <= number <= 300:
        return "Part XII"
    if 301 <= number <= 307:
        return "Part XIII"
    if number == 323 and suffix in ("A", "B"):
        return "Part XIVA"
    if 308 <= number <= 323:
        return "Part XIV"
    if 324 <= number <= 329:
        return "Part XV"
    if 330 <= number <= 342:
        return "Part XVI"
    if 343 <= number <= 351:
        return "Part XVII"
    if 352 <= number <= 360:
        return "Part XVIII"
    if 361 <= number <= 367:
        return "Part XIX"
    if number == 368:
        return "Part XX"
    if 369 <= number <= 392:
        return "Part XXI"
    if 393 <= number <= 395:
        return "Part XXII"

    return "Not identified"


def extract_pdf_text():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))
    print("Total PDF pages:", len(reader.pages))

    page_texts = []

    for page_number, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned_text = join_wrapped_lines(raw_text)

        if cleaned_text:
            page_texts.append({
                "page": page_number,
                "text": cleaned_text
            })

    return page_texts


def get_page_for_position(position, page_ranges):
    for item in page_ranges:
        if item["start"] <= position < item["end"]:
            return item["page"]

    return 0


def article_sort_key(article_no):
    match = re.fullmatch(r"(\d+)([A-Z]?)", article_no.upper())

    if not match:
        return -1, ""

    return int(match.group(1)), match.group(2)



def parse_articles(page_texts):
    """Extract individual articles, starting from actual Article 1 text."""

    # Find the actual Article 1 page, not the Table of Contents.
    start_page_index = None

    for i, item in enumerate(page_texts):
        text = item["text"]

        if (
            "Name and territory of the Union" in text
            and "shall be a Union of States" in text
        ):
            start_page_index = i
            break

    if start_page_index is None:
        raise ValueError("Actual Article 1 text not found.")

    # Ignore all pages before actual Article 1.
    actual_pages = page_texts[start_page_index:]

    full_text = ""
    page_ranges = []

    for item in actual_pages:
        start = len(full_text)
        full_text += item["text"] + " "
        end = len(full_text)

        page_ranges.append({
            "start": start,
            "end": end,
            "page": item["page"]
        })

    # Article headings must end with an em dash or en dash.
    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"(?P<number>\d{1,3}[A-Z]?)\.\s+"
        r"(?P<title>[A-Z][^—–]{2,180}?)"
        r"\s*[—–]"
    )

    matches = list(pattern.finditer(full_text))

    valid_matches = []
    last_key = (-1, "")

    for match in matches:
        article_no = match.group("number")
        current_key = article_sort_key(article_no)

        if current_key > last_key:
            valid_matches.append(match)
            last_key = current_key

    records = []

    for index, match in enumerate(valid_matches):
        article_no = match.group("number")
        title = match.group("title").strip(" .")

        content_start = match.end()

        content_end = (
            valid_matches[index + 1].start()
            if index + 1 < len(valid_matches)
            else len(full_text)
        )

        article_text = full_text[content_start:content_end].strip()

        source_page = get_page_for_position(
            match.start(),
            page_ranges
        )

        if not title or len(article_text) < 10:
            continue

        records.append(
            Record(
                article_no=article_no,
                title=title,
                part=get_part(article_no),
                text=article_text,
                amended_by=[],
                source_page=source_page
            )
        )

    print("Article headings detected:", len(valid_matches))

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
    print("Total article records:", len(records))


def main():
    print("Starting SamvidhanSathi PDF ingestion...")

    page_texts = extract_pdf_text()
    print("Extracting Constitution articles...")

    records = parse_articles(page_texts)

    if not records:
        raise ValueError("No valid article records extracted.")

    save_records(records)

    print("\nFirst 10 extracted articles:")

    for record in records[:10]:
        print(
            f"\nArticle {record.article_no}: {record.title}\n"
            f"Part: {record.part}\n"
            f"Text: {record.text[:250]}\n"
            f"Page: {record.source_page}"
        )

    article_21 = next(
        (record for record in records if record.article_no == "21"),
        None
    )

    if article_21:
        print("\nARTICLE 21 CHECK")
        print("Title:", article_21.title)
        print("Text:", article_21.text[:500])


if __name__ == "__main__":
    main()
