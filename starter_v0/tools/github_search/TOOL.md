---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, sort, max_results]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches public GitHub repositories via the official GitHub REST API
(`https://api.github.com/search/repositories`). Optionally uses `GITHUB_TOKEN`
if set in the environment for higher rate limits, but works without any API key.

