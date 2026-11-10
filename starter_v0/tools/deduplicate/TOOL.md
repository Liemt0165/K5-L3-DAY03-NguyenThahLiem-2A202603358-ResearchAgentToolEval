---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, input_count, removed_count]
side_effect: false
---
# deduplicate

Removes repeated source URLs from an already-collected list, keeping the first
item and its original metadata. Does not search, fetch, summarize or verify claims.

Normalizes host casing, default ports, empty root paths, query parameter ordering;
ignores fragments and tracking parameters utm_*, fbclid, gclid. Keeps meaningful
query parameters, path casing, trailing path slashes, and http vs https distinct.
Does not resolve redirects or detect paraphrases of the same story.

Empty list returns an empty result. Missing list, invalid item, non-http(s) URL,
or malformed port returns an error dictionary, never partial success or a raised
exception. No network or filesystem access; no API key needed.
