"""Campaign screen for the sales outreach agent.

Opens a sequencer-style page in the browser. The agent writes a three-email
sequence for each lead in data/leads.csv (research, first email, two
follow-ups), and you watch each step finish. Nothing goes out until a
person approves it, and the screen only ever does a dry run. Real sending
stays behind the explicit --send flag in process_leads.py.

Run:
    python app.py
"""

import json
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from agent.email_sender import send_email
from agent.llm import DEFAULT_MODEL
from agent.outreach import build_graph
from process_leads import load_leads

load_dotenv()

logger = logging.getLogger("sales-outreach")
app = FastAPI(title="AI Sales Outreach Agent")
WEB_DIR = Path(__file__).resolve().parent / "web"
_graph = None


class Lead(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    title: str = Field(default="", max_length=120)
    company: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=200)
    notes: str = Field(default="none", max_length=1000)


class Approval(BaseModel):
    to: str = Field(min_length=3, max_length=200)
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=5000)


def stream_sequence(lead: dict):
    """Run the outreach graph for one lead, yielding (step, update) as each
    node finishes: research, draft_initial, draft_followups."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    for chunk in _graph.stream({"lead": lead}, stream_mode="updates"):
        yield from chunk.items()


@app.get("/", include_in_schema=False)
def campaign():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/info")
def info():
    return {"model": os.getenv("LLM_MODEL") or DEFAULT_MODEL, "research": "Tavily web search" if os.getenv("TAVILY_API_KEY") else "Local notes (data/company_notes.json)"}


@app.get("/api/leads")
def leads():
    return load_leads()


@app.post("/api/sequence")
def sequence(lead: Lead):
    """Newline-delimited JSON, one line per finished step, then a done line."""
    def lines():
        started = time.perf_counter()
        try:
            for step, update in stream_sequence(lead.model_dump()):
                yield json.dumps({"step": step, **update}) + "\n"
            yield json.dumps({"done": True, "seconds": round(time.perf_counter() - started, 1)}) + "\n"
        except Exception as exc:
            logger.exception("Sequence failed for %s", lead.email)
            detail = str(exc).splitlines()[0][:200] if str(exc) else ""
            yield json.dumps({"error": f"The agent could not finish this sequence ({type(exc).__name__}: {detail})."}) + "\n"

    return StreamingResponse(lines(), media_type="application/x-ndjson")


@app.post("/api/approve")
def approve(body: Approval):
    """Approve the first email. Always a dry run from the browser."""
    return {"status": send_email(to=body.to, subject=body.subject, body=body.body, dry_run=True)}


if __name__ == "__main__":
    import threading
    import webbrowser

    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    uvicorn.run(app, host="127.0.0.1", port=port)
