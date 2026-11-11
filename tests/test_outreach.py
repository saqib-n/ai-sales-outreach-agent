import pytest

from agent import outreach
from agent.email_sender import send_email
from agent.research import research_company
from process_leads import build_row
from tests.fakes import FakeStructuredLLM

LEAD = {"name": "Maria Gonzalez", "title": "Head of Operations", "company": "Acme Robotics",
        "email": "maria@example.com", "notes": "none"}


def test_research_uses_local_notes_without_a_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    assert "warehouse automation" in research_company("Acme Robotics")
    assert "No specific research" in research_company("Unknown Co")


def test_dry_run_is_the_default():
    assert send_email("a@example.com", "Hi", "Body").startswith("[DRY RUN]")


def test_real_send_without_smtp_settings_fails_clearly(monkeypatch):
    for name in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match="SMTP_HOST"):
        send_email("a@example.com", "Hi", "Body", dry_run=False)


def test_email_is_signed_with_sender_name(monkeypatch):
    monkeypatch.setenv("SENDER_NAME", "Saqib")
    llm = FakeStructuredLLM(outreach.EmailDraft(subject="s", body="b"))
    result = outreach.draft_initial_node({"lead": LEAD, "research": "r"}, llm)
    assert result == {"initial_email": {"subject": "s", "body": "b"}}
    system_prompt = llm.calls[0][0].content
    assert "Sign off as Saqib." in system_prompt


def test_csv_row_survives_missing_followups():
    result = {"initial_email": {"subject": "s", "body": "b"}, "followups": [{"subject": "f1", "body": "x"}]}
    row = build_row(LEAD, result, approved=False, send_status="not sent")
    assert row["followup_1_subject"] == "f1"
    assert row["followup_2_subject"] == ""
