# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy bài đăng từ một tài khoản X cụ thể | không |
| social_search | tìm bài đăng X theo chủ đề | không |
| lookup | tìm thông tin và tin tức trên web | không |
| fetch | đọc nội dung URL do người dùng cung cấp | không |
| format | định dạng các nguồn đã thu thập thành digest | không |
| send | gửi digest lên Telegram sau khi xác nhận | không |
| policy | tra cứu chính sách nội bộ | không |
| papers | tìm bài báo trên arXiv | không |
| paper_text | trích văn bản từ bài arXiv | không |
| github_search | tìm repository công khai theo từ khóa/ngôn ngữ | có (v2) |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Starter behavior established a 65% base baseline | — | 65% (13/20) | `runs/v0_B_base_openrouter_20261110T115945025570.json` |
| v1 | `system_prompt.md` | Clarification, confirmation, and concise query rules improve routing | 65% | 100% (20/20) | `runs/v1_B_base_openai_20261110T114712007209.json` |
| v2 | `system_prompt.md`, `tools.yaml`, `github_search` | Add public repository search and distinguish it from web news | 100% | 80% (16/20) | `runs/v2_B_base_openrouter_20261110T121453310623.json` |
| v3 | `system_prompt.md` | Explicit priority for missing targets, send confirmation, and latest-turn intent resolves observed v2 failures | 80% | 100% base (20/20); group eval pending | `runs/v3_B_base_openrouter_20261110T124406560221.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `social_search(query="", ...)` | Guessed a topic search instead of asking which account | v3 explicitly clarifies when both account and topic are missing; PASS in v3 base |
| R11_missing_url | missing_info | `fetch(url="https://example.com")` | Invented a URL instead of asking for the article link | v3 prohibits guessed URLs; PASS in v3 base |
| R12_confirm_before_send | wrong_boundary | `clarify(response_type="text")` | Asked for content before confirming the external action | v3 prioritizes yes/no action confirmation and separately requires confirmation of exact content; PASS in v3 base |
| M06_switch_tool | wrong_tool | `social_search(query="OpenAI", search_type="Top")` | Kept social-search intent instead of switching to web news | v3 makes the latest-turn intent authoritative; PASS in v3 base |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_github_search_python_research_agents | GitHub routing, language, stars, limit | github_search | Đang chạy live eval |
| G02_github_search_recent_rust_vector_databases | language, updated sort, limit | github_search | Đang chạy live eval |
| G03_github_search_sort_by_forks | fork sort and limit | github_search | Đang chạy live eval |
| G04_web_news_not_github | Distinguishes web news from repository search | lookup | Đang chạy live eval |
| G05_meta_question_no_tool | No unnecessary tool call | No tool | Đang chạy live eval |
| G06_multiturn_add_github_language_filter | Carries topic and adds language | github_search | Đang chạy live eval |
| G07_multiturn_correct_language_and_sort | Applies latest language, sort, and limit | github_search | Đang chạy live eval |
| G08_multiturn_change_github_result_limit | Carries topic and updates limit | github_search | Đang chạy live eval |
| G09_multiturn_switch_github_search_to_news | Latest intent changes tool | lookup | Đang chạy live eval |
| G10_multiturn_switch_account_tweets_to_topic_top_posts | Switches timeline to topic search | social_search | Đang chạy live eval |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest -c starter_v0/pytest.ini starter_v0/tests -q` | 18 test mới trong `test_tools_todo.py`; toàn suite 85 passed, 0 skipped | Offline suite xanh |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
