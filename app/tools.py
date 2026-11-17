import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLE_MAP = BASE_DIR / "data" / "article_map.csv"


def article_key(article_no):
    """Convert article number into a comparable numeric and suffix pair."""
    article_no = str(article_no).strip().upper()

    match = re.fullmatch(r"(\d+)([A-Z]*)", article_no)

    if not match:
        raise ValueError("Invalid article number. Example: 21A or 243ZH")

    return int(match.group(1)), match.group(2)


def get_neighbours(article_no):
    """Return the previous and next numbered article labels."""
    number, suffix = article_key(article_no)

    if not suffix:
        return str(number - 1), str(number + 1)

    if suffix == "A":
        return str(number), str(number + 1)

    previous_suffix = suffix[:-1] + chr(ord(suffix[-1]) - 1)
    next_suffix = suffix[:-1] + chr(ord(suffix[-1]) + 1)

    return (
        f"{number}{previous_suffix}",
        f"{number}{next_suffix}"
    )


def locate_article(article_no):
    """Find the Part and details for a Constitution article number."""
    try:
        target = article_key(article_no)
    except ValueError as error:
        return {"found": False, "message": str(error)}

    with open(ARTICLE_MAP, "r", encoding="utf-8-sig", newline="") as file:
        rows = csv.DictReader(file, skipinitialspace=True)
        rows.fieldnames = [name.strip().lstrip("\ufeff") for name in rows.fieldnames]

        for row in rows:
            start = article_key(row["range_start"])
            end = article_key(row["range_end"])

            if start <= target <= end:
                previous, next_article = get_neighbours(article_no)

                return {
                    "found": True,
                    "article": str(article_no).strip().upper(),
                    "part": row["part"],
                    "part_name": row["part_name"],
                    "chapter": row["chapter"] or "Not applicable",
                    "title": row["title"],
                    "article_range": (
                        f'{row["range_start"]}–{row["range_end"]}'
                    ),
                    "neighbouring_articles": {
                        "previous": previous,
                        "next": next_article
                    }
                }

    return {
        "found": False,
        "article": str(article_no).strip().upper(),
        "message": "Article number is not covered in the article map."
    }