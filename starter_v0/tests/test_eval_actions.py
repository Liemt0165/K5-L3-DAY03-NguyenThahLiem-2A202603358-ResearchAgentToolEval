from agent import ResearchAgent
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS


def test_eval_records_send_call_but_does_not_execute_it(monkeypatch):
    def forbidden(**kwargs):
        raise AssertionError("Publishing must not run during eval")

    monkeypatch.setitem(TOOL_FUNCTIONS, "send", forbidden)

    class Provider:
        def complete(self, *args, **kwargs):
            return ModelResponse(text=None, tool_calls=[ToolCall("send", {"text": "Draft", "confirmed": True})])

    result = ResearchAgent(Provider(), system_prompt="test", blocked_tools={"send"}).run([])
    assert result.tool_calls[0].name == "send"
    assert result.tool_results[0]["result"]["status"] == "execution_disabled"
