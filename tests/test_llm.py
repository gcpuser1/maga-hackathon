"""The model route: the pinned model name must be one that Pydantic AI can resolve."""

from logfire.testing import CaptureLogfire
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models import infer_model
from pydantic_ai.models.function import AgentInfo, FunctionModel
import pytest

from maga import llm


class _Answer(BaseModel):
    ok: bool


def test_the_pinned_model_is_a_gemini_model_that_pydantic_ai_knows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key")  # resolving builds the provider
    model = infer_model(llm.MODEL)
    assert (model.system, model.model_name) == ("google", "gemini-3.8-flash")


def test_a_model_call_is_traced_and_the_trace_holds_no_secret(capfire: CaptureLogfire) -> None:
    def respond(_messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {"ok": True})])

    secret = "API_KEY=" + "FAKE_SECRET_VALUE_001"
    assert llm.ask(_Answer, "Answer ok.", f"export {secret}", FunctionModel(respond)).ok
    spans = capfire.exporter.exported_spans_as_dict()
    assert any("agent" in span["name"] for span in spans), [span["name"] for span in spans]
    assert "FAKE_SECRET_VALUE_001" not in str(spans)
    assert "[REDACTED_SECRET]" in str(spans)
