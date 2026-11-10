"""Check initial UI, a real OpenAI chat turn, transcript, and reset.

Run manually; this spends one live chat turn and is not part of offline pytest.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
assert not app.exception, app.exception
assert app.title[0].value == "Research Agent"
assert app.chat_input and not app.chat_input[0].disabled
app.chat_input[0].set_value("Tra cứu policy nội bộ: quy định trích dẫn nguồn yêu cầu gì?").run(timeout=90)
assert not app.exception, app.exception
turn = app.session_state["transcript"]["turns"][-1]
assert turn["status"] != "provider_error", turn
assert turn["assistant_text"]
assert any(event["tool"] == "policy" for event in turn["tool_events"]), turn
transcript_path = ROOT / "transcripts" / f"{app.session_state['transcript']['transcript_id']}.transcript.json"
assert transcript_path.exists()
print("PASS: initial UI, live OpenAI policy tool, rendered answer, saved transcript")
print(f"Transcript: {transcript_path}")
app.sidebar.button[0].click().run()
assert not app.exception
assert app.session_state["transcript"]["turns"] == []
print("PASS: reset conversation")
