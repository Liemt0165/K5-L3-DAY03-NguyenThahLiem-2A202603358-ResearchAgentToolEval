r"""Streamlit interface for the Research Agent artifact versions.

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

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
VERSION_FILES = {
    "v1": (ROOT / "artifacts" / "versions" / "v1" / "system_prompt.md",
           ROOT / "artifacts" / "versions" / "v1" / "tools.yaml"),
    "v2": (ROOT / "artifacts" / "versions" / "v2" / "system_prompt.md",
           ROOT / "artifacts" / "versions" / "v2" / "tools.yaml"),
    "v3": (ROOT / "artifacts" / "system_prompt.md", ROOT / "artifacts" / "tools.yaml"),
}
VERSION_NOTES = {
    "v1": "Prompt NTL: routing, clarify và query discipline.",
    "v2": "v1 + deduplicate + contract tests + group eval.",
    "v3": "v2 + latest-turn guardrails + safe draft confirmation.",
}


def version_paths(version: str) -> tuple[Path, Path]:
    try:
        return VERSION_FILES[version]
    except KeyError as exc:
        raise ValueError(f"Unsupported artifact version: {version}") from exc


def new_session(version: str, prompt_path: Path, tools_path: Path) -> dict:
    return {
        "transcript_id": f"{version}_ui_{datetime.now():%Y%m%dT%H%M%S}_{uuid4().hex[:8]}",
        **artifact_version_dict(build_artifact_version(version, prompt_path, tools_path)),
        "provider": "openai", "model": MODEL, "interface": "streamlit",
        "created_at": now_iso(), "turns": [],
    }


def reset_session(version: str) -> None:
    prompt_path, tools_path = version_paths(version)
    st.session_state.transcript = new_session(version, prompt_path, tools_path)
    st.session_state.selected_version = version


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon=":material/search:", layout="wide")
    if "selected_version" not in st.session_state:
        st.session_state.selected_version = "v3"

    with st.sidebar:
        st.markdown("## Research Agent")
        st.caption("Artifact playground · OpenAI-compatible provider")
        selected_version = st.selectbox(
            "Artifact version",
            list(VERSION_FILES),
            index=list(VERSION_FILES).index(st.session_state.selected_version),
            format_func=lambda value: f"{value}  ·  {VERSION_NOTES[value].split(' + ')[0]}",
        )
        if selected_version != st.session_state.selected_version:
            reset_session(selected_version)
            st.rerun()

        prompt_path, tools_path = version_paths(selected_version)
        artifact = build_artifact_version(selected_version, prompt_path, tools_path)
        st.info(VERSION_NOTES[selected_version])
        st.caption(f"Artifact: `{artifact.artifact_version}`")
        st.divider()
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            reset_session(selected_version)
            st.rerun()
        if "transcript" not in st.session_state:
            reset_session(selected_version)
        transcript = st.session_state.transcript
        st.download_button(
            "Tải transcript JSON",
            json.dumps(transcript, ensure_ascii=False, indent=2),
            file_name=f"{transcript['transcript_id']}.transcript.json",
            mime="application/json", use_container_width=True,
        )
        st.divider()
        st.markdown("**Kết nối dịch vụ**")
        for label, key in [
            ("OpenAI", "OPENAI_API_KEY"),
            ("Tìm web · Tavily", "TAVILY_API_KEY"),
            ("Đọc URL · Firecrawl", "FIRECRAWL_API_KEY"),
            ("Twitter/X · RapidAPI", "RAPIDAPI_KEY"),
        ]:
            state = "đã có key" if os.getenv(key) else "chưa có key"
            st.caption(f"{label}  ·  {state}")

    if "transcript" not in st.session_state:
        reset_session(selected_version)
    transcript = st.session_state.transcript
    declarations = load_tool_declarations(tools_path)
    st.title("Research Agent")
    st.caption(f"{selected_version} · {MODEL} · {len(declarations)} tools · transcript tự lưu")
    st.write("Chọn artifact version ở thanh bên để so sánh cách prompt và tool declaration ảnh hưởng đến routing.")

    if not transcript["turns"]:
        st.info("Bắt đầu bằng một yêu cầu nghiên cứu. Chọn v1, v2 hoặc v3 trước khi gửi câu hỏi.")
        with st.expander("Câu hỏi gợi ý", expanded=True):
            st.markdown(
                "- Lọc các URL trùng trong danh sách nguồn đã có.\n"
                "- Tìm 3 tweet phổ biến nhất về Anthropic trên X.\n"
                "- Đọc và tóm tắt bài này giúp tôi."
            )

    for turn in transcript["turns"]:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn["status"] == "provider_error":
                st.error(turn["assistant_text"])
            else:
                st.markdown(turn["assistant_text"] or "Agent chưa trả về nội dung.")
            if turn.get("tool_events"):
                with st.expander(f"Xem {len(turn['tool_events'])} lần gọi tool"):
                    st.json(turn["tool_events"])

    has_key = bool(os.getenv("OPENAI_API_KEY"))
    query = st.chat_input("Nhập yêu cầu nghiên cứu…", disabled=not has_key)
    if not has_key:
        st.warning("Thiếu OPENAI_API_KEY. Điền key trong .env rồi khởi động lại UI.")
    if query:
        history = []
        for turn in transcript["turns"]:
            if turn["status"] != "provider_error":
                history.extend([
                    {"role": "user", "content": turn["user"]},
                    {"role": "assistant", "content": turn["assistant_text"]},
                ])
        record = {"turn_index": len(transcript["turns"]) + 1, "user": query, "started_at": now_iso()}
        with st.chat_message("user"):
            st.write(query)
        try:
            with st.spinner(f"Đang xử lý bằng {selected_version}…"):
                result = run_model_tool_loop(
                    provider=make_provider("openai"),
                    messages=[
                        {"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
                        *trim_history(history, 5),
                        {"role": "user", "content": query},
                    ],
                    tools=to_openai_tools(declarations), model=MODEL, max_tool_rounds=4,
                )
            record.update(result)
        except Exception:
            record.update(
                status="provider_error",
                assistant_text="Không kết nối được OpenAI. Kiểm tra key, số dư và kết nối mạng rồi thử lại.",
                rounds=[], tool_events=[],
            )
        record["ended_at"] = now_iso()
        transcript["turns"].append(record)
        write_transcript(ROOT / "transcripts" / f"{transcript['transcript_id']}.transcript.json", transcript)
        st.rerun()


if __name__ == "__main__":
    main()
