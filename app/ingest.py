
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
    r"\s*(?:\.)?\s*[—–]\s*"
)


def join_wrapped_lines(text):
    """Join wrapped PDF lines while keeping readable spacing."""
    lines = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return " ".join(lines)


def get_part(article_no):
    """Identify the Constitution Part using article number ranges."""

    match = re.fullmatch(r"(\d+)([A-Z]*)", str(article_no).upper())

    if not match:
        return "Not identified"

    number = int(match.group(1))
    suffix = match.group(2)

    if number <= 4:
        return "Part I"
    elif number <= 11:
        return "Part II"
    elif number <= 35:
        return "Part III"
    elif number <= 51:
        return "Part IV"
    elif number == 51 and suffix == "A":
        return "Part IVA"
    elif 52 <= number <= 151:
        return "Part V"
    elif 152 <= number <= 237:
        return "Part VI"
    elif 238 <= number <= 242:
        return "Part VIII"
    elif number == 243:
        if suffix == "":
            return "Part IX"
        if suffix == "P" or suffix.startswith(("Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")):
            return "Part IXA"
    elif 244 <= number <= 244:
        return "Part X"
    elif 245 <= number <= 263:
        return "Part XI"
    elif 264 <= number <= 300:
        return "Part XII"
    elif 301 <= number <= 307:
        return "Part XIII"
    elif 308 <= number <= 323:
        return "Part XIV"
    elif number == 323 and suffix in ("A", "B"):
        return "Part XIVA"
    elif 324 <= number <= 329:
        return "Part XV"
    elif 330 <= number <= 342:
        return "Part XVI"
    elif 343 <= number <= 351:
        return "Part XVII"
    elif 352 <= number <= 360:
        return "Part XVIII"
    elif 361 <= number <= 367:
        return "Part XIX"
    elif number == 368:
        return "Part XX"
    elif 369 <= number <= 392:
        return "Part XXI"
    elif 393 <= number <= 395:
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
    """Find the PDF page containing a text position."""

    for page_range in page_ranges:
        if page_range["start"] <= position < page_range["end"]:
            return page_range["page"]

    return 0


def article_sort_key(article_no):
    """Create a sortable key for article numbers such as 21 and 21A."""

    match = re.fullmatch(r"(\d+)([A-Z]*)", article_no.upper())

    if not match:
        return -1, ""

    return int(match.group(1)), match.group(2)


def parse_articles(page_texts):
    """Extract actual article headings and their corresponding text."""

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

    matches = list(ARTICLE_PATTERN.finditer(full_text))

    # Ignore table-of-contents entries and start from Article 1.
    start_index = None

    for i, match in enumerate(matches):
        article_no = match.group("number")
        title = match.group("title").strip(" .")

        if (
            article_no == "1"
            and title.lower().startswith("name and territory of the union")
        ):
            start_index = i
            break

    if start_index is None:
        raise ValueError(
            "Could not find the actual Article 1 heading. "
            "Check the PDF text extraction."
        )

    matches = matches[start_index:]

    # Remove false matches from footnotes and other text
    # by keeping article numbers in increasing order.
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

        if index + 1 < len(valid_matches):
            content_end = valid_matches[index + 1].start()
        else:
            content_end = len(full_text)

        article_text = full_text[content_start:content_end].strip()

        # Remove common amendment-footnote text from the end.
        footnote_pattern = re.compile(
            r"\s+\d+\.\s+"
            r"(?:Ins\. by|Subs\. by|Omitted by|"
            r"The words|Certain words|Cl\.)",
            re.IGNORECASE
        )

        footnote_match = footnote_pattern.search(article_text)

        if footnote_match:
            article_text = article_text[:footnote_match.start()].strip()

        source_page = get_page_for_position(
            match.start(),
            page_ranges
        )

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

    print("Extracting Constitution articles...")

    records = parse_articles(page_texts)

    if not records:
        raise ValueError("No valid article records were extracted.")

    save_records(records)

    print("\nFirst 10 extracted articles:")

    for record in records[:10]:
        print("\nArticle:", record.article_no)
        print("Title:", record.title)
        print("Part:", record.part)
        print("Text:", record.text[:200])
        print("Source page:", record.source_page)

    article_21 = next(
        (r for r in records if r.article_no == "21"),
        None
    )

    if article_21:
        print("\nARTICLE 21 CHECK")
        print("Title:", article_21.title)
        print("Text:", article_21.text[:500])


if __name__ == "__main__":
    main()
