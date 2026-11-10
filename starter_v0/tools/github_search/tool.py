
from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def github_search(
    query: str = "",
    language: str = "",
    sort: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    """
    Search public GitHub repositories.

    Args:
        query: Search keywords. Must not be empty.
        language: Optional programming language filter.
        sort: stars, forks, or updated.
        limit: Number of repositories to return (1-100).
    """
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        if not isinstance(language, str):
            raise ValueError("language must be a string")

        if sort not in {"stars", "forks", "updated"}:
            raise ValueError("sort must be stars, forks, or updated")

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit must be an integer")

        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        search_query = query.strip()
        if language.strip():
            search_query += f" language:{language.strip()}"

        response = requests.get(
            GITHUB_SEARCH_URL,
            params={
                "q": search_query,
                "sort": sort,
                "order": "desc",
                "per_page": limit,
            },
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "ResearchAgentToolEval",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        repositories = []
        for item in data.get("items", []):
            repositories.append({
                "name": item.get("full_name"),
                "description": item.get("description"),
                "url": item.get("html_url"),
                "language": item.get("language"),
                "stars": item.get("stargazers_count"),
                "forks": item.get("forks_count"),
                "updated_at": item.get("updated_at"),
            })

        return {
            "tool": "github_search",
            "query": query,
            "language": language,
            "sort": sort,
            "total_count": data.get("total_count", 0),
            "items": repositories,
        }

    except Exception as exc:
        return err("github_search", exc)
