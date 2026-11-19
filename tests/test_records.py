
from app.records import load_records, search, count_by, get_by_id


def test_load_records_returns_list():
    records = load_records()
    assert isinstance(records, list)


def test_load_records_not_empty():
    assert len(load_records()) > 0


def test_search_finds_existing_article():
    records = load_records()
    first_record = records[0]

    results = search(records, first_record["title"])

    assert first_record in results


def test_count_by_matches_total_records():
    records = load_records()
    counts = count_by(records)

    assert sum(counts.values()) == len(records)


def test_get_by_id_existing_article():
    records = load_records()
    article_no = records[0]["article_no"]

    result = get_by_id(records, article_no)

    assert result is not None
    assert result["article_no"] == article_no


def test_get_by_id_missing_article():
    records = load_records()

    assert get_by_id(records, "999999") is None
