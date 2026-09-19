"""The model route: the pinned model name must be one that Pydantic AI can resolve."""

from pydantic_ai.models import infer_model
import pytest

from maga import llm


def test_the_pinned_model_is_a_gemini_model_that_pydantic_ai_knows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key")  # resolving builds the provider
    model = infer_model(llm.MODEL)
    assert (model.system, model.model_name) == ("google", "gemini-3.8-flash")
