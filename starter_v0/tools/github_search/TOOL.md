
---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort, limit]
outputs: [total_count, items]
side_effect: false
---

# github_search

Searches public GitHub repositories using the GitHub REST API.

## When to use
- When the user asks to find GitHub repositories.
- When the user wants examples of projects using a framework or programming language.
- When the user wants to compare public repositories by stars, forks, or update time.

## When NOT to use
- Do not use for searching general web pages or news.
- Do not use for reading the source code of a specific repository.
- Do not use for private repositories or account-specific information.

## Arguments
- `query`: Required search keywords. Must not be empty.
- `language`: Optional programming language filter, such as JavaScript or Python.
- `sort`: `stars`, `forks`, or `updated`.
- `limit`: Number of results, from 1 to 100.

## Output
Each repository contains:
- name
- description
- url
- language
- stars
- forks
- updated_at
