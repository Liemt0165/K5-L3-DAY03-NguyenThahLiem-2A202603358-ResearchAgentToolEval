"""Remove repeated source URLs without merging unrelated articles."""
from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def _canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Each item needs an absolute http(s) URL")
    if parts.username or parts.password:
        raise ValueError("URLs containing credentials are not supported")
    host = parts.hostname.lower()
    port = parts.port
    if ":" in host:
        host = f"[{host}]"
    if port and (parts.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
        host += f":{port}"
    query = sorted((key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
                   if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"})
    return urlunsplit((parts.scheme.lower(), host, parts.path or "/", urlencode(query), ""))


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per normalized URL. Validate all input before returning."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of objects with nonempty url strings")
        seen: set[str] = set()
        unique = []
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("url"), str):
                raise ValueError("Each item must be an object with a nonempty url string")
            key = _canonical_url(item["url"])
            if key not in seen:
                seen.add(key)
                unique.append(dict(item))
        return {"tool": "deduplicate", "items": unique, "input_count": len(items),
                "removed_count": len(items) - len(unique)}
    except Exception as exc:
        return {"tool": "deduplicate", "error": type(exc).__name__, "message": str(exc)}
