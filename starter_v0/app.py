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

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"
VERSION = "v2"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")


def new_session() -> dict:
    return {
        "transcript_id": f"{VERSION}_ui_{datetime.now():%Y%m%dT%H%M%S}_{uuid4().hex[:8]}",
        **artifact_version_dict(build_artifact_version(VERSION, PROMPT, TOOLS)),
        "provider": "openai", "model": MODEL, "interface": "streamlit",
        "created_at": now_iso(), "turns": [],
    }


def main() -> None:
    st.set_page_config(page_title=f"Research Agent · {VERSION}", page_icon=":material/search:", layout="centered")
    if "transcript" not in st.session_state:
        st.session_state.transcript = new_session()
    if (st.session_state.transcript.get("artifact_version") != build_artifact_version(VERSION, PROMPT, TOOLS).artifact_version
            or st.session_state.transcript.get("model") != MODEL):
        # Previous turns have already been persisted; do not mix artifact versions.
        st.session_state.transcript = new_session()
    transcript = st.session_state.transcript
    declarations = load_tool_declarations(TOOLS)

    with st.sidebar:
        st.header("Phiên nghiên cứu")
        st.caption(f"OpenAI · {MODEL} · {VERSION}")
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            st.session_state.transcript = new_session()
            st.rerun()
        st.download_button(
            "Tải transcript JSON",
            json.dumps(transcript, ensure_ascii=False, indent=2),
            file_name=f"{transcript['transcript_id']}.transcript.json",
            mime="application/json", use_container_width=True,
        )
        st.subheader("Kết nối dịch vụ")
        for label, key in [("OpenAI", "OPENAI_API_KEY"), ("Tìm web · Tavily", "TAVILY_API_KEY"),
                           ("Đọc URL · Firecrawl", "FIRECRAWL_API_KEY"), ("Twitter/X · RapidAPI", "RAPIDAPI_KEY")]:
            st.text(f"{label}: {'đã có key' if os.getenv(key) else 'chưa có key'}")
        st.caption("Trạng thái chỉ kiểm tra cấu hình, không xác thực key. Bổ sung key trong .env rồi khởi động lại UI.")
        with st.expander(f"{len(declarations)} tool có sẵn"):
            for tool in declarations:
                st.markdown(f"**{tool['name']}** — {tool['description']}")
        st.caption("v2 xây từ prompt v1 của NTL; thêm deduplicate, 10 case nhóm và unit test. Xem kết quả trong runs.")

    st.title("Research Agent")
    st.write("Tìm nguồn, đọc tài liệu và theo dõi cách agent sử dụng công cụ.")
    st.caption("v2 · Nền v1 NTL · GPT-5.4 · Transcript tự lưu")
    if not transcript["turns"]:
        st.info("Bắt đầu bằng một câu hỏi. Với cấu hình hiện tại, bạn có thể thử tra cứu policy nội bộ hoặc định dạng dữ liệu có sẵn.")
        with st.expander("Câu hỏi gợi ý", expanded=True):
            st.markdown("- Chính sách nội bộ yêu cầu trích dẫn nguồn như thế nào?\n- Bạn là gì và có những công cụ nào?\n- Tin AI hôm nay có gì? *(cần key Tavily để lấy dữ liệu)*")

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

    query = st.chat_input("Nhập yêu cầu nghiên cứu…", disabled=not bool(os.getenv("OPENAI_API_KEY")))
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Thiếu OPENAI_API_KEY. Điền key trong .env và khởi động lại UI.")
    if query:
        history = []
        for turn in transcript["turns"]:
            if turn["status"] != "provider_error":
                history.extend([{"role": "user", "content": turn["user"]},
                                {"role": "assistant", "content": turn["assistant_text"]}])
        record = {"turn_index": len(transcript["turns"]) + 1, "user": query, "started_at": now_iso()}
        with st.chat_message("user"):
            st.write(query)
        try:
            with st.spinner("Agent đang xử lý yêu cầu…"):
                result = run_model_tool_loop(
                    provider=make_provider("openai"),
                    messages=[{"role": "system", "content": PROMPT.read_text(encoding="utf-8")},
                              *trim_history(history, 5), {"role": "user", "content": query}],
                    tools=to_openai_tools(declarations), model=MODEL, max_tool_rounds=4,
                )
            record.update(result)
        except Exception:
            # Raw provider exceptions can contain request details; keep them out of UI/transcripts.
            record.update(status="provider_error", assistant_text="Không kết nối được OpenAI. Kiểm tra key, số dư và kết nối mạng rồi thử lại.", rounds=[], tool_events=[])
        record["ended_at"] = now_iso()
        transcript["turns"].append(record)
        try:
            write_transcript(ROOT / "transcripts" / f"{transcript['transcript_id']}.transcript.json", transcript)
        except OSError:
            st.error("Không lưu được transcript vào ổ đĩa. Bạn vẫn có thể tải JSON ở thanh bên.")
            st.stop()
        st.rerun()


if __name__ == "__main__":
    main()
