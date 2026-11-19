
from app import smart_search


def test_search_records_finds_matching_article(monkeypatch):
    sample = [
        {
            "article_no": "21",
            "title": "Right to Life",
            "part": "Part III",
            "text": "No person shall be deprived of life or personal liberty."
        },
        {
            "article_no": "14",
            "title": "Right to Equality",
            "part": "Part III",
            "text": "Equality before the law."
        }
    ]

    monkeypatch.setattr(smart_search, "load_records", lambda: sample)

    results = smart_search.search_records("personal liberty")

    assert len(results) > 0
    assert results[0]["article_no"] == "21"


def test_search_records_empty_query(monkeypatch):
    monkeypatch.setattr(
        smart_search,
        "load_records",
        lambda: [{"title": "Test", "part": "Part III", "text": "Sample"}]
    )

    assert smart_search.search_records("   ") == []


def test_search_records_respects_limit(monkeypatch):
    sample = [
        {
            "article_no": str(i),
            "title": f"Right {i}",
            "part": "Part III",
            "text": f"Constitutional provision number {i}"
        }
        for i in range(1, 4)
    ]

    monkeypatch.setattr(smart_search, "load_records", lambda: sample)

    results = smart_search.search_records("constitutional provision", limit=2)

    assert len(results) <= 2
