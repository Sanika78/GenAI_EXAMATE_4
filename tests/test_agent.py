
import pytest

from app.tools import article_key, locate_article


def test_article_key_parses_normal_article():
    assert article_key("21") == (21, "")


def test_article_key_parses_amended_article():
    assert article_key("21A") == (21, "A")


def test_article_key_rejects_invalid_input():
    with pytest.raises(ValueError):
        article_key("ABC")


def test_locate_article_finds_article_21a():
    result = locate_article("21A")

    assert result["found"] is True
    assert result["article"] == "21A"
    assert result["part"] == "Part III"
