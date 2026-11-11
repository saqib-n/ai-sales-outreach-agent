"""Company research, real web search if a Tavily key is set, otherwise a
local fallback so the whole project still runs with just an LLM key.

Swap this for a real research pipeline (Tavily, SerpAPI, Clearbit, whatever
a client already pays for) on an actual engagement, the rest of the agent
doesn't need to change.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _mock_research(company: str) -> str:
    with open(DATA_DIR / "company_notes.json", "r", encoding="utf-8") as f:
        notes = json.load(f)
    return notes.get(
        company.strip().lower(),
        f"No specific research found for {company}. Keep the message general "
        "but still reference their name and role directly.",
    )


def research_company(company: str) -> str:
    """Return a short block of context about a company.

    Uses Tavily search if TAVILY_API_KEY is set in the environment,
    otherwise falls back to the local company_notes.json file so the
    project runs without a search API key.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return _mock_research(company)

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        result = client.search(
            query=f"{company} company overview recent news",
            max_results=3,
        )
        snippets = [item.get("content", "") for item in result.get("results", [])]
        combined = " ".join(snippets).strip()
        return combined if combined else _mock_research(company)
    except Exception:
        # Search API hiccup shouldn't block the whole pipeline, fall back.
        return _mock_research(company)
