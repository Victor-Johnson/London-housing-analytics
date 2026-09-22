from types import SimpleNamespace

from app import briefing_generator


class FakeCompletions:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        message = SimpleNamespace(content="Mocked briefing text.")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_generate_briefing_returns_completion_text(monkeypatch):
    fake_completions = FakeCompletions()
    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))
    monkeypatch.setattr(briefing_generator, "get_client", lambda: fake_client)

    rising = [("Hackney", "Greater London", 500000, 12.0, 40)]
    falling = [("Barking", "Greater London", 250000, -8.0, 30)]

    result = briefing_generator.generate_briefing("2024-01-01", rising, falling)

    assert result == "Mocked briefing text."


def test_generate_briefing_includes_district_data_in_prompt(monkeypatch):
    fake_completions = FakeCompletions()
    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))
    monkeypatch.setattr(briefing_generator, "get_client", lambda: fake_client)

    rising = [("Hackney", "Greater London", 500000, 12.0, 40)]
    falling = [("Barking", "Greater London", 250000, -8.0, 30)]

    briefing_generator.generate_briefing("2024-01-01", rising, falling)

    prompt = fake_completions.last_kwargs["messages"][0]["content"]
    assert "Hackney" in prompt
    assert "Barking" in prompt
    assert "2024-01-01" in prompt
