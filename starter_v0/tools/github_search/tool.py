from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
ALLOWED_SORTS = {"stars", "updated", "forks", "help-wanted-issues"}


def search_github_repos(
    query: str = "",
    sort: str = "stars",
    max_results: int = 5,
) -> dict[str, Any]:
    """Search public GitHub repositories by keyword/topic."""
    cleaned_query = " ".join((query or "").split())
    if not cleaned_query:
        return {
            "tool": "github_search",
            "error": "ValueError",
            "message": "query must not be empty.",
            "items": [],
        }

    try:
        try:
            limit = max(1, min(int(max_results or 5), 10))
        except (TypeError, ValueError):
            limit = 5

        normalized_sort = sort if sort in ALLOWED_SORTS else "stars"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AI20k-Day03-Research-Agent/1.0",
        }
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        params: dict[str, Any] = {
            "q": cleaned_query,
            "sort": normalized_sort,
            "order": "desc",
            "per_page": limit,
        }
        response = requests.get(
            GITHUB_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        items: list[dict[str, Any]] = []
        for repo in (payload.get("items") or [])[:limit]:
            if not isinstance(repo, dict):
                continue
            full_name = repo.get("full_name") or repo.get("name") or ""
            html_url = repo.get("html_url") or ""
            if not full_name or not html_url:
                continue
            description = " ".join(str(repo.get("description") or "").split())
            items.append({
                "title": full_name,
                "url": html_url,
                "source": "github.com",
                "summary": description or "No description provided.",
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "language": repo.get("language"),
                "updated_at": repo.get("updated_at"),
                "topics": list(repo.get("topics") or []),
            })

        return {
            "tool": "github_search",
            "query": cleaned_query,
            "sort": normalized_sort,
            "total_count": int(payload.get("total_count") or len(items)),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)

