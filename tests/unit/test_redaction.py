from src.application.redaction import RedactingProvider, redact_text
from src.domain.llm import CompletionRequest, Message
from src.infrastructure.providers.fake import FakeLLMProvider


def test_redactor_masks_email_phone_and_national_id():
    text = redact_text("mail a@example.com call +201001234567 id 12345678901234")
    assert "a@example.com" not in text
    assert "+201001234567" not in text
    assert "12345678901234" not in text


def test_provider_redacts_completion_and_embedding_inputs():
    provider = FakeLLMProvider()
    wrapped = RedactingProvider(provider)
    wrapped.complete(
        CompletionRequest(messages=(Message("user", "contact a@example.com"),))
    )
    wrapped.embed(["contact a@example.com"])

    _, request = provider.calls[0]
    assert "a@example.com" not in request.prompt_text()
    assert "a@example.com" not in provider.calls[1][1][0]
