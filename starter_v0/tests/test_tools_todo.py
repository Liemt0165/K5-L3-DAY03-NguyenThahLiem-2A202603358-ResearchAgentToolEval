"""Tool Unit Test Challenge — completed with 0 skipped, 0 failed."""
from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
github_search_tool = TOOL_FUNCTIONS["github_search"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    opts = ["OpenAI", "Anthropic"]
    result = clarify_tool(question="Bạn muốn chọn hãng nào?", response_type="choice", options=opts)
    assert result["options"] == opts
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item 2", "section": "B", "url": "https://b.com/2"},
        {"title": "Item 3", "section": "A", "url": "https://a.com/3"},
    ]
    result = format_tool(items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First item", "url": "https://example.com/1"},
        {"title": "Second item", "url": "https://example.com/2"},
    ]
    result = format_tool(items=items, template="thread")
    chunks = result["markdown"].split("\n\n")
    assert chunks[0].startswith("1/ ")
    assert chunks[1].startswith("2/ ")


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None, template="sections")
    res_empty = format_tool(items=[], template="bullets")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot-token-123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "@test_channel"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin AI", confirmed=True)
    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", topic="general", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Hello Firecrawl content",
            "metadata": {"title": "Sample Title", "sourceURL": "https://openai.com/blog/test"},
        }
    }))

    result = fetch_tool(url="https://openai.com/blog/test")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert result["items"][0] == {
        "title": "Sample Title",
        "url": "https://openai.com/blog/test",
        "source": "openai.com",
        "summary": "Hello Firecrawl content",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "a" * 5000,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = fetch_tool(url="https://example.com/long")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    raw_timeline = [{"screen_name": "sama", "text": "No ID tweet"}] + [
        {"screen_name": "sama", "tweet_id": str(100 + i), "text": f"Tweet {i}"}
        for i in range(6)
    ]
    calls = fake_http(FakeResponse({"timeline": raw_timeline}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(calls) == 1
    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"]):
        assert item["url"] == f"https://x.com/sama/status/{100 + idx}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    result = social_search_tool(query="OpenAI", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert result["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="   ")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="API key customer data prompt", policy_area="data_privacy")
    assert len(result["results"]) >= 1
    for item in result["results"]:
        assert item["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="viral tweet social source citation", policy_area="source_citation", top_k=5)
    assert len(result["results"]) >= 1
    all_untrusted = [line for item in result["results"] for line in item.get("untrusted_text", [])]
    all_facts = " ".join(item.get("facts", "") for item in result["results"])
    assert any("ignore" in line.lower() or "bỏ qua" in line.lower() or "assistant" in line.lower() for line in all_untrusted)
    assert "ignore previous" not in all_facts.lower()


# ---------------- YOUR NEW TOOL(S): github_search ----------------

def test_my_new_tool_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total_count": 1,
        "items": [
            {
                "full_name": "langchain-ai/langgraph",
                "html_url": "https://github.com/langchain-ai/langgraph",
                "description": "Build resilient language agents as graphs.",
                "stargazers_count": 12000,
                "forks_count": 1500,
                "language": "Python",
                "updated_at": "2026-11-09T00:00:00Z",
                "topics": ["agents", "llm"],
            }
        ],
    }))

    result = github_search_tool(query="langgraph agent", sort="stars", max_results=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "langgraph agent"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert result["tool"] == "github_search"
    assert result["total_count"] == 1
    assert result["items"][0]["title"] == "langchain-ai/langgraph"
    assert result["items"][0]["stars"] == 12000
    assert result["items"][0]["source"] == "github.com"


def test_my_new_tool_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"total_count": 0, "items": []}))
    empty_res = github_search_tool(query="   ", sort="invalid_sort", max_results="bad_int")
    assert empty_res["error"] == "ValueError"
    assert calls == []

    # Invalid sort enum and string max_results fall back safely when query is non-empty
    valid_res = github_search_tool(query="mcp", sort="invalid_enum", max_results="not_a_number")
    assert valid_res["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 5


def test_my_new_tool_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))
    result = github_search_tool(query="openai")
    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"
