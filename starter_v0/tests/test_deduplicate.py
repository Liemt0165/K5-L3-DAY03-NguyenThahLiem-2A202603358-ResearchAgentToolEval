"""Offline behavior and error cases for the new research tool."""
import pytest

from tools.deduplicate.tool import deduplicate_sources


def test_deduplicate_ignores_tracking_and_keeps_first_metadata():
    items = [{"url": "https://EXAMPLE.com/a?utm_source=x&id=1#top", "title": "First"},
             {"url": "https://example.com/a?id=1", "title": "Second"}]
    result = deduplicate_sources(items)
    assert result["items"] == [items[0]]
    assert result["input_count"] == 2
    assert result["removed_count"] == 1
    assert len(items) == 2


def test_deduplicate_preserves_different_articles_and_meaningful_queries():
    items = [{"url": url} for url in ["https://example.com/a?id=1", "https://example.com/a?id=2",
                                      "http://example.com/a?id=1", "https://example.com/A?id=1"]]
    result = deduplicate_sources(items)
    assert result["items"] == items
    assert result["removed_count"] == 0


def test_deduplicate_empty_list():
    assert deduplicate_sources([])["items"] == []


@pytest.mark.parametrize("items", [None, "bad", [{}], [None], [{"url": ""}], [{"url": 42}],
                                   [{"url": "file:///a"}], [{"url": "https://example.com:bad/"}],
                                   [{"url": "https://user:password@example.com/"}]])
def test_deduplicate_bad_input_returns_error_not_partial_results(items):
    result = deduplicate_sources(items)
    assert result["error"] == "ValueError"
    assert "items" not in result


def test_deduplicate_normalizes_default_port_root_and_query_order():
    result = deduplicate_sources([{"url": "https://EXAMPLE.com:443?b=2&a=1"},
                                  {"url": "https://example.com/?a=1&b=2"}])
    assert result["removed_count"] == 1


def test_deduplicate_internal_failure_returns_error_dict(monkeypatch):
    import tools.deduplicate.tool as module

    def fail(url):
        raise RuntimeError("normalization unavailable")

    monkeypatch.setattr(module, "_canonical_url", fail)
    result = deduplicate_sources([{"url": "https://example.com"}])
    assert result["error"] == "RuntimeError"
    assert result["message"] == "normalization unavailable"
