from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent — Tool Eval Lab",
    page_icon="🔬",
    layout="wide",
)

SAMPLE_PROMPTS = [
    ("💻 GitHub (Tool mới)", "Tìm giúp mình các repo GitHub mã nguồn mở nhiều sao nhất về MCP server."),
    ("🐦 Timeline", "Lấy 3 tweet mới nhất của Sam Altman"),
    ("🔥 Social Search", "Cho mình các tweet phổ biến (top) nhất về OpenAI"),
    ("📰 Web News", "Tin tức AI hôm nay có gì nổi bật?"),
    ("📚 arXiv Papers", "Tìm paper arXiv về retrieval augmented generation evaluation."),
    ("🛡️ Company Policy", "Theo company policy, tweet viral có được coi là fact đã xác nhận không?"),
    ("❓ Clarify (Thiếu handle)", "Tóm tắt 5 tweet mới nhất giúp mình"),
    ("📨 Telegram (Xác nhận trước khi gửi)", "Đăng bản tin này lên Telegram giúp mình: OpenAI vừa ra mắt mô hình mới."),
]


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
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
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


def main() -> None:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    declarations = load_tool_declarations(tools_path)

    with st.sidebar:
        st.title("⚙️ Cấu hình Agent")
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
        version_label = st.text_input("Version Label", value="v3")
        history_window = st.slider("History Window (turns)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=6, value=4)

        init_session_state(provider_name, model_input.strip() or None, version_label.strip() or "v3")

        if st.button("🔄 Tạo phiên hội thoại mới", use_container_width=True):
            st.session_state.pop("config_key", None)
            init_session_state(provider_name, model_input.strip() or None, version_label.strip() or "v3")
            st.rerun()

        st.divider()
        st.subheader("🧪 Câu hỏi mẫu (1-Click Demo)")
        for label, sample_query in SAMPLE_PROMPTS:
            if st.button(label, help=sample_query, use_container_width=True):
                st.session_state.pending_prompt = sample_query

        st.divider()
        with st.expander(f"🧰 Danh sách Tools ({len(declarations)})", expanded=False):
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

    artifact_version = build_artifact_version(version_label.strip() or "v3", system_prompt_path, tools_path)
    st.title("🔬 AI Research Agent — Live Tool Evaluation UI")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Artifact Version", artifact_version.artifact_version)
    col2.metric("Provider / Model", f"{provider_name} ({model_input or 'default'})")
    col3.metric("Declared Tools", len(declarations))
    col4.metric("Turns Logged", len(st.session_state.ui_turns))

    st.divider()

    if not st.session_state.ui_turns:
        st.info(
            "👋 Nhập câu hỏi nghiên cứu ở khung chat bên dưới hoặc bấm vào **Câu hỏi mẫu (1-Click Demo)** ở thanh bên trái để thử các tool (`lookup`, `timeline`, `social_search`, `fetch`, `github_search`, `papers`, `policy`, `clarify`, `send`)."
        )

    for turn in st.session_state.ui_turns:
        with st.chat_message("user"):
            st.markdown(turn["user"])

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

    # Quick-action buttons when waiting for user confirmation/choices
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

    user_input = st.chat_input("Nhập yêu cầu nghiên cứu của bạn...")
    prompt_to_run = st.session_state.pop("pending_prompt", None) or user_input

    if prompt_to_run:
        with st.spinner("🤖 Agent đang suy luận và gọi tool..."):
            process_user_turn(
                prompt_to_run,
                provider_name=provider_name,
                model_name=model_input.strip() or None,
                version_label=version_label.strip() or "v3",
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
            )
        st.rerun()


if __name__ == "__main__":
    main()

