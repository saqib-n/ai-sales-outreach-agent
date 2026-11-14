import json

from fastapi.testclient import TestClient

import app as web
from agent import outreach
from tests.fakes import FakeStructuredLLM


def test_campaign_streams_steps_and_approval_is_a_dry_run(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    llm = FakeStructuredLLM(
        outreach.EmailDraft(subject="Faster fulfilment at Acme", body="Hi Maria..."),
        outreach.FollowupSequence(followups=[outreach.EmailDraft(subject="f1", body="b1"), outreach.EmailDraft(subject="f2", body="b2")]),
    )
    monkeypatch.setattr(web, "_graph", outreach.build_graph(llm=llm))
    client = TestClient(web.app)

    assert "Write all sequences" in client.get("/").text
    leads = client.get("/api/leads").json()
    assert len(leads) == 4

    lead = {k: leads[0][k] for k in ("name", "title", "company", "email", "notes")}
    lines = [json.loads(line) for line in client.post("/api/sequence", json=lead).text.splitlines() if line]
    assert [m.get("step") for m in lines[:3]] == ["research", "draft_initial", "draft_followups"]
    assert "warehouse automation" in lines[0]["research"]
    assert lines[1]["initial_email"]["subject"] == "Faster fulfilment at Acme"
    assert len(lines[2]["followups"]) == 2 and lines[3]["done"] is True

    sent = client.post("/api/approve", json={"to": lead["email"], "subject": "s", "body": "b"}).json()
    assert sent["status"].startswith("[DRY RUN]")
