from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

from agent import ResearchAgent
from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)

r"""Streamlit interface for the current research agent artifacts.

Run: .venv\Scripts\python -m streamlit run app.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

<<<<<<< HEAD
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent — Tool Eval Lab (v0 → v3)",
    page_icon="🔬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Historical snapshots for v0, v1, v2 so you can live-demo and compare any
# version side-by-side! v3 always reads the live files in artifacts/.
# ---------------------------------------------------------------------------
V0_SYSTEM_PROMPT = """You are a fast, proactive research assistant with access to tools.

The user is busy and hates being asked questions. Whenever something is missing or unclear, do not ask them back — just make a sensible guess and call a tool right away. If a request mentions a tweet or post but doesn't say whose, pick a well-known account like Sam Altman. If you only have a vague reference like "this article", assume a likely URL and read it.

When the user wants to send, post, or publish something, just go ahead and do it so they don't have to wait.

Always finish the request in a single step. Pick one tool and fill in its arguments using your best judgment."""

V1_SYSTEM_PROMPT = """You are a careful, evidence-driven AI & technology research assistant.

Follow these strict rules:
1. Scope & No-Tool Boundary:
   - Only assist with news, social media, web articles, research papers, and company policies.
   - If the user asks about your identity/capabilities (meta questions) or out-of-scope tasks (math problems, coding/programming exercises, general homework), DO NOT call any tool. Reply directly in text (politely refuse out-of-scope requests).

2. Missing Information (Never Guess):
   - Never guess or fabricate a Twitter/X handle, URL, or topic.
   - If the user asks for someone's tweets without specifying whose account/handle, call `clarify` with `response_type="text"`.
   - If the user asks to read/summarize "this article/link" without providing a URL, call `clarify` with `response_type="text"`.

3. Confirmation Before Sending (`send`):
   - Never call `send` to post/publish to Telegram unless the user has explicitly confirmed in the conversation.
   - When the user first asks to post/send something to Telegram, call `clarify` with `response_type="yes_no"` to ask for confirmation first.

4. Tool Routing & Multi-tool:
   - Call multiple tools in parallel when the user asks for multiple sources (e.g. both web news and Twitter posts).
   - In multi-turn conversations, carry over relevant context from earlier turns, apply user corrections, and only execute the latest turn."""

V2_SYSTEM_PROMPT = """You are an expert research assistant with access to specialized tools.

Operating Principles & Tool Usage:

Scope & Direct Answers:
For meta-questions about yourself or out-of-scope tasks (coding, math, personal advice), respond directly. DO NOT call any tool.
Only call tools when external research, data retrieval, or formatting is genuinely required.

Handling Missing Information:
NEVER hallucinate, guess, or assume missing parameters.
If a request requires a specific target (such as an article URL or an account handle) that the user omitted, call {clarify} with response_type="text".

Action Confirmation (Safety Guardrail):
For external publishing or messaging actions (e.g., {send}), NEVER execute without explicit user approval.
Always call {clarify} with response_type="yes_no" to obtain user confirmation before sending. Only call {send} once confirmed (confirmed=True).

Tool Routing & Query Discipline:
Use {fetch} when given an explicit URL (url).
Use {timeline} for posts published by a specific person/account. Use clean usernames (strip any leading '@').
Use {social_search} for community discussions on a topic. Set search_type="Top" if popular/top posts are requested.
Use {lookup} for general web info or news. Set topic="news" and appropriate timeframe when searching recent events.
Concise Queries: Keep query strictly focused on the core subject/entity. Do not duplicate temporal words ("news", "today", "latest") into query when timeframe or topic parameters already capture them.

Multi-turn Context:
Always prioritize corrections, new limits, or intent shifts from the latest turn."""

V0_V1_TOOLS_YAML = """tools:
  - name: clarify
    description: "Gửi một câu hỏi cho người dùng."
    parameters:
      type: object
      properties:
        question: {type: string, default: "", description: "Câu hỏi"}
        response_type: {type: string, enum: [text, yes_no, choice], default: "text", description: "Kiểu trả lời"}
        options: {type: array, default: [], items: {type: string}, description: "Các lựa chọn"}
      required: [question]
  - name: timeline
    description: "Lấy các bài đăng gần đây."
    parameters:
      type: object
      properties:
        screenname: {type: string, default: "", description: "Tên tài khoản"}
        limit: {type: integer, default: 5, description: "Số lượng"}
      required: [screenname]
  - name: social_search
    description: "Tìm trên mạng xã hội."
    parameters:
      type: object
      properties:
        query: {type: string, default: "", description: "Từ khóa"}
        search_type: {type: string, enum: [Latest, Top], default: "Latest", description: "Cách sắp xếp"}
        limit: {type: integer, default: 5, description: "Số lượng"}
      required: [query]
  - name: lookup
    description: "Tra cứu thông tin trên internet."
    parameters:
      type: object
      properties:
        query: {type: string, default: "", description: "Truy vấn"}
        topic: {type: string, enum: [general, news], default: "general", description: "Phân loại"}
        timeframe: {type: string, enum: [day, week, month, year], default: "week", description: "Khoảng thời gian"}
        max_results: {type: integer, default: 5, description: "Số kết quả"}
      required: [query]
  - name: fetch
    description: "Lấy nội dung từ một địa chỉ."
    parameters:
      type: object
      properties:
        url: {type: string, default: "", description: "Địa chỉ"}
      required: [url]
  - name: format
    description: "Trình bày dữ liệu đã có thành văn bản."
    parameters:
      type: object
      properties:
        items:
          type: array
          default: []
          description: "Danh sách item"
          items:
            type: object
            properties:
              title: {type: string}
              url: {type: string}
              source: {type: string}
              summary: {type: string}
              section: {type: string}
        template: {type: string, enum: [brief, sections, bullets, thread, daily_ai_vn], default: "sections", description: "Khuôn"}
        headline: {type: string, default: "", description: "Tiêu đề"}
      required: [items, template]
  - name: send
    description: "Gửi một đoạn văn bản đi."
    parameters:
      type: object
      properties:
        text: {type: string, default: "", description: "Nội dung"}
        confirmed: {type: boolean, default: false, description: "Cờ xác nhận"}
      required: [text]
  - name: policy
    description: "Tìm trong tài liệu nội bộ."
    parameters:
      type: object
      properties:
        query: {type: string, default: "", description: "Truy vấn"}
        policy_area: {type: string, enum: [all, ai_research, source_citation, data_privacy, external_publishing, tool_usage], default: "all", description: "Nhóm"}
        top_k: {type: integer, default: 3, description: "Số mục"}
      required: [query]
  - name: papers
    description: "Tìm bài báo khoa học."
    parameters:
      type: object
      properties:
        query: {type: string, default: "", description: "Từ khóa"}
        max_results: {type: integer, default: 5, description: "Số lượng"}
        sort_by: {type: string, enum: [relevance, lastUpdatedDate, submittedDate], default: "relevance", description: "Sắp xếp"}
      required: [query]
  - name: paper_text
    description: "Lấy nội dung text của một bài báo."
    parameters:
      type: object
      properties:
        arxiv_url: {type: string, default: "", description: "ID hoặc địa chỉ"}
        max_pages: {type: integer, default: 5, description: "Số trang"}
        max_chars: {type: integer, default: 8000, description: "Số ký tự"}
      required: [arxiv_url]
"""

SAMPLE_PROMPTS = [
    ("💻 GitHub (Tool mới)", "Tìm giúp mình các repo GitHub mã nguồn mở nhiều sao nhất về MCP server."),
    ("🐦 Timeline (Map tên -> handle)", "Tweet mới nhất của Sam Altman là gì?"),
    ("🔥 Social Search (Top)", "Cho mình các tweet phổ biến (top) nhất về OpenAI"),
    ("📰 Web News (Hôm nay)", "Tin tức AI hôm nay có gì nổi bật?"),
    ("📚 arXiv Papers", "Tìm paper arXiv về retrieval augmented generation evaluation."),
    ("🛡️ Company Policy", "Theo company policy, tweet viral có được coi là fact đã xác nhận không?"),
    ("❓ Clarify (Thiếu handle)", "Tóm tắt 5 tweet mới nhất giúp mình"),
    ("📨 Telegram (Xác nhận trước khi gửi)", "Đăng bản tin này lên Telegram giúp mình"),
    ("🚫 Out-of-scope (Toán/Code)", "Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?"),
]


def get_version_bundle(version_label: str) -> tuple[str, list[dict[str, Any]], str]:
    """Return (system_prompt, tool_declarations, description) for v0, v1, v2, or v3."""
    live_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    live_tools = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    v0_tools = yaml.safe_load(V0_V1_TOOLS_YAML)["tools"]

    if version_label == "v0":
        return (
            V0_SYSTEM_PROMPT,
            v0_tools,
            "v0 (Baseline gốc: prompt xúi đoán mò & tự gửi, tools.yaml sơ sài)",
        )
    if version_label == "v1":
        return (
            V1_SYSTEM_PROMPT,
            v0_tools,
            "v1 (Đã sửa system_prompt.md: biết clarify & chặn out-of-scope, nhưng tools.yaml vẫn sơ sài)",
        )
    if version_label == "v2":
        return (
            V2_SYSTEM_PROMPT,
            live_tools,
            "v2 (Đã viết chi tiết tools.yaml: biết map Sam Altman -> sama & đọc URL)",
        )
    return (
        live_prompt,
        live_tools,
        "v3 (Bản tối ưu nhất hiện tại trong artifacts/ + đầy đủ các Tool mới)",
    )


def init_session_state(provider_name: str, model_name: str | None, version_label: str) -> None:
    config_key = f"{provider_name}:{model_name or 'default'}:{version_label}"
    if st.session_state.get("config_key") == config_key and "transcript" in st.session_state:
        return

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"

    st.session_state.config_key = config_key
    st.session_state.history = []
    st.session_state.ui_turns = []
    st.session_state.turn_index = 0
    st.session_state.transcript_path = transcript_path
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def process_user_turn(
    user_text: str,
    *,
    provider_name: str,
    model_name: str | None,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    system_prompt, declarations, _ = get_version_bundle(version_label)
    openai_tools = to_openai_tools(declarations)
    provider = make_provider(provider_name)
    resolved_model = model_name or getattr(provider, "default_model", None)
    st.session_state.transcript["model"] = resolved_model
    st.session_state.transcript["history_window"] = history_window
    st.session_state.transcript["max_tool_rounds"] = max_tool_rounds

    st.session_state.turn_index += 1
    turn_index = st.session_state.turn_index
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "version": version_label,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model_name or None,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {str(exc)}",
            "assistant_text": f"❌ Lỗi Provider: `{type(exc).__name__}: {str(exc)}`",
        })

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    st.session_state.ui_turns.append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


def load_saved_runs() -> list[dict[str, Any]]:
    runs_dir = ROOT / "runs"
    if not runs_dir.exists():
        return []
    loaded: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_filename"] = path.name
            loaded.append(data)
        except Exception:
            continue
    return loaded


def render_chat_tab(
    provider_name: str,
    model_input: str,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    _, declarations, ver_desc = get_version_bundle(version_label)
    st.info(f"🎯 **Phiên bản đang chạy:** `{version_label}` — {ver_desc} ({len(declarations)} tools)")

    for turn in st.session_state.ui_turns:
        with st.chat_message("user"):
            st.markdown(f"**[{turn.get('version', version_label)}]** {turn['user']}")

        with st.chat_message("assistant"):
            tool_events = turn.get("tool_events", [])
            if tool_events:
                for idx, event in enumerate(tool_events, start=1):
                    t_name = event.get("tool", "unknown")
                    t_args = event.get("args", {})
                    t_res = event.get("result", {})
                    is_err = isinstance(t_res, dict) and ("error" in t_res)
                    badge = "❌" if is_err else "🔧"
                    with st.expander(
                        f"{badge} Bước {idx}: `{t_name}({json.dumps(t_args, ensure_ascii=False)})`",
                        expanded=(turn == st.session_state.ui_turns[-1]),
                    ):
                        st.markdown("**Arguments:**")
                        st.json(t_args)
                        st.markdown("**Result:**")
                        st.json(t_res)
            else:
                st.caption("⚡ *Trả lời trực tiếp (không gọi tool)*")

            if turn.get("status") == "waiting_for_user":
                st.warning(f"⏸️ **Agent đang chờ bạn xác nhận / bổ sung thông tin:**\n\n{turn.get('assistant_text', '')}")
            else:
                st.markdown(turn.get("assistant_text") or "")

    if st.session_state.ui_turns:
        last_turn = st.session_state.ui_turns[-1]
        if last_turn.get("status") == "waiting_for_user" and last_turn.get("tool_events"):
            last_res = last_turn["tool_events"][-1].get("result", {})
            resp_type = last_res.get("response_type", "text")
            if resp_type == "yes_no":
                b_col1, b_col2, _ = st.columns([1, 1, 3])
                if b_col1.button("✅ Đồng ý, gửi đi nhé", use_container_width=True):
                    st.session_state.pending_prompt = "Đồng ý, gửi đi nhé"
                    st.rerun()
                if b_col2.button("❌ Không, hủy bỏ", use_container_width=True):
                    st.session_state.pending_prompt = "Thôi hủy đi, đừng gửi nữa"
                    st.rerun()
            elif resp_type == "choice" and last_res.get("options"):
                cols = st.columns(len(last_res["options"]))
                for c_idx, opt in enumerate(last_res["options"]):
                    if cols[c_idx].button(str(opt), use_container_width=True):
                        st.session_state.pending_prompt = str(opt)
                        st.rerun()

    user_input = st.chat_input(f"Nhập câu hỏi cho Agent ({version_label})...")
    prompt_to_run = st.session_state.pop("pending_prompt", None) or user_input

    if prompt_to_run:
        with st.spinner(f"🤖 Agent ({version_label}) đang suy luận và gọi tool..."):
            process_user_turn(
                prompt_to_run,
                provider_name=provider_name,
                model_name=model_input.strip() or None,
                version_label=version_label,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
            )
        st.rerun()


def render_side_by_side_tab(provider_name: str, model_input: str) -> None:
    st.subheader("⚔️ So sánh trực tiếp hành vi `v0` vs `v1` vs `v2` vs `v3` trên cùng 1 câu hỏi")
    st.caption(
        "Chọn một câu hỏi bẫy bên dưới và bấm **Chạy so sánh** để thấy sự khác biệt rõ rệt về Tool Routing & Arguments giữa các phiên bản."
    )

    presets = {
        "R10 (Thiếu handle): Tóm tắt 5 tweet mới nhất giúp mình": "Tóm tắt 5 tweet mới nhất giúp mình",
        "R11 (Thiếu URL): Tóm tắt bài viết này hộ mình": "Tóm tắt bài viết này hộ mình",
        "R12 (Chưa confirm gửi): Đăng bản tin này lên Telegram giúp mình": "Đăng bản tin này lên Telegram giúp mình",
        "R01 (Map tên -> handle): Tweet mới nhất của Sam Altman là gì?": "Tweet mới nhất của Sam Altman là gì?",
        "R04 (Đã có URL): Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5": "Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5",
        "R08 (Ngoài phạm vi): Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?": "Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?",
        "G01 (Tool mới GitHub): Tìm giúp mình các repo GitHub mã nguồn mở nhiều sao nhất về MCP server.": "Tìm giúp mình các repo GitHub mã nguồn mở nhiều sao nhất về MCP server.",
    }
    selected_preset = st.selectbox("Chọn kịch bản kiểm thử nhanh:", list(presets.keys()))
    compare_query = st.text_input("Hoặc tự nhập câu hỏi cần so sánh:", value=presets[selected_preset])
    selected_versions = st.multiselect(
        "Chọn các phiên bản muốn chạy so sánh:",
        options=["v0", "v1", "v2", "v3"],
        default=["v0", "v1", "v2", "v3"],
    )

    if st.button("🚀 Chạy so sánh trực tiếp", type="primary") and compare_query.strip() and selected_versions:
        provider = make_provider(provider_name)
        cols = st.columns(len(selected_versions))
        for idx, ver in enumerate(selected_versions):
            with cols[idx]:
                st.markdown(f"### Phiên bản `{ver}`")
                sys_prompt, decls, desc = get_version_bundle(ver)
                st.caption(desc)
                with st.spinner(f"Đang chạy {ver}..."):
                    try:
                        agent = ResearchAgent(
                            provider,
                            system_prompt=sys_prompt,
                            tools=to_openai_tools(decls),
                            model=model_input.strip() or None,
                        )
                        run = agent.run([{"role": "user", "content": compare_query.strip()}])
                        if run.tool_calls:
                            for call in run.tool_calls:
                                st.success(f"🔧 Tool: **`{call.name}`**")
                                st.json(call.args)
                        else:
                            st.info("⚡ Không gọi tool (Trả lời trực tiếp)")
                        if run.text:
                            st.markdown("**Phản hồi text:**")
                            st.write(run.text)
                    except Exception as exc:
                        st.error(f"Lỗi: {type(exc).__name__}: {exc}")


def render_eval_dashboard_tab() -> None:
    st.subheader("📊 Bảng tổng hợp lịch sử tối ưu (`artifacts/version_log.csv` & `runs/*.json`)")

    vlog_path = ARTIFACTS_DIR / "version_log.csv"
    if vlog_path.exists():
        rows = list(csv.DictReader(vlog_path.read_text(encoding="utf-8").splitlines()))
        if rows:
            st.markdown("#### 1. Nhật ký Version (`version_log.csv`)")
            st.dataframe(rows, use_container_width=True)

    runs = load_saved_runs()
    if not runs:
        st.warning("Chưa có file kết quả nào trong `runs/*.json`.")
        return

    st.markdown("#### 2. Bảng chỉ số Accuracy qua các lần chạy (`runs/*.json`)")
    summary_rows = []
    for r in runs:
        s = r.get("summary", {})
        summary_rows.append({
            "Version": r.get("version"),
            "Suite": r.get("suite"),
            "Provider / Model": f"{r.get('provider')} ({r.get('model')})",
            "Case Accuracy": s.get("case_accuracy"),
            "Routing Accuracy": s.get("tool_routing_accuracy"),
            "Arg Accuracy": s.get("argument_accuracy"),
            "Multiturn Accuracy": s.get("multiturn_accuracy"),
            "Passed / Measured": f"{s.get('passed_cases')}/{s.get('measured_cases')}",
            "Run File": r.get("_filename"),
        })
    st.dataframe(summary_rows, use_container_width=True)

    st.markdown("#### 3. So sánh chi tiết PASS / FAIL từng câu giữa các Run")
    run_Map = {f"{r.get('version')} ({r.get('_filename')})": r for r in runs}
    chosen_labels = st.multiselect(
        "Chọn các file Run để đối chiếu từng case:",
        options=list(run_Map.keys()),
        default=list(run_Map.keys()),
    )
    if chosen_labels:
        case_ids: list[str] = []
        for label in chosen_labels:
            for item in run_Map[label].get("results", []):
                if item["id"] not in case_ids:
                    case_ids.append(item["id"])

        comparison_table = []
        for cid in case_ids:
            row: dict[str, Any] = {"Case ID": cid}
            for label in chosen_labels:
                matched = next((x for x in run_Map[label].get("results", []) if x["id"] == cid), None)
                if not matched:
                    row[label] = "—"
                else:
                    res = matched.get("result", {})
                    calls_str = ", ".join(
                        f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})"
                        for c in res.get("actual_tool_calls", [])
                    ) or "no_tool"
                    status = "✅ PASS" if res.get("passed") else f"❌ FAIL ({res.get('observed_mismatch') or res.get('failure_type')})"
                    row[label] = f"{status} → {calls_str}"
            comparison_table.append(row)
        st.dataframe(comparison_table, use_container_width=True, height=550)


def main() -> None:
    with st.sidebar:
        st.title("⚙️ Cấu hình Agent")
        version_label = st.selectbox(
            "Chọn Phiên bản (Version) để chạy:",
            options=["v3", "v2", "v1", "v0"],
            index=0,
            help="Bạn có thể chọn v0, v1, v2, hoặc v3 để chạy thử hành vi của từng phiên bản!",
        )
        provider_name = st.selectbox(
            "Provider",
            options=["openrouter", "openai", "gemini", "anthropic", "ollama"],
            index=0,
        )
        default_models = {
            "openrouter": "openai/gpt-4o-mini",
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.5-flash",
            "anthropic": "claude-3-5-haiku-latest",
            "ollama": "qwen2.5:7b",
        }
        model_input = st.text_input("Model", value=default_models.get(provider_name, ""))
        history_window = st.slider("History Window (turns)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=6, value=4)

        init_session_state(provider_name, model_input.strip() or None, version_label)

        if st.button("🔄 Xóa hội thoại / Tạo phiên mới", use_container_width=True):
            st.session_state.pop("config_key", None)
            init_session_state(provider_name, model_input.strip() or None, version_label)
            st.rerun()

        st.divider()
        st.subheader("🧪 Câu hỏi mẫu (1-Click Demo)")
        for label, sample_query in SAMPLE_PROMPTS:
            if st.button(label, help=sample_query, use_container_width=True):
                st.session_state.pending_prompt = sample_query

        _, declarations, _ = get_version_bundle(version_label)
        st.divider()
        with st.expander(f"🧰 Tools của `{version_label}` ({len(declarations)})", expanded=False):
            for item in declarations:
                st.markdown(f"**`{item['name']}`**")
                st.caption(item.get("description", "").strip())

        st.divider()
        st.subheader("📝 Transcript Log")
        transcript_path: Path = st.session_state.transcript_path
        st.caption(f"File: `transcripts/{transcript_path.name}`")
        st.download_button(
            "⬇️ Tải Transcript JSON",
            data=json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str),
            file_name=transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    _, active_decls, _ = get_version_bundle(version_label)

    st.title("🔬 AI Research Agent — Live Tool Evaluation & Version Comparison")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Version", version_label.upper())
    col2.metric("Provider / Model", f"{provider_name} ({model_input or 'default'})")
    col3.metric("Tools in Version", len(active_decls))
    col4.metric("Turns Logged", len(st.session_state.ui_turns))

    tab_chat, tab_compare, tab_dashboard = st.tabs([
        "💬 Chat Live (Chạy theo Version đang chọn)",
        "⚔️ So sánh trực tiếp v0 vs v1 vs v2 vs v3",
        "📊 Bảng điểm & Phân tích Runs (v0 → v3)",
    ])

    with tab_chat:
        render_chat_tab(provider_name, model_input, version_label, history_window, max_tool_rounds)

    with tab_compare:
        render_side_by_side_tab(provider_name, model_input)

    with tab_dashboard:
        render_eval_dashboard_tab()

if __name__ == "__main__":
    main()
