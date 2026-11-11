"""LangGraph pipeline for one lead: research -> draft first email -> draft
follow-up sequence.

This is a straight line, not a branching agent, because the steps always
happen in the same order for every lead. LangGraph is still worth using
here for the same reason it was worth using in the other projects: the
state is explicit, each step is a small testable function, and it's easy
to add a branch later (e.g. skip research for leads that already have
notes) without restructuring everything.
"""

import os
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from agent.llm import get_llm
from agent.research import research_company


class EmailDraft(BaseModel):
    subject: str = Field(description="Short, specific email subject line, not generic")
    body: str = Field(description="The email body, 3-5 short sentences, plain text")


class FollowupSequence(BaseModel):
    followups: list[EmailDraft] = Field(description="Exactly 2 follow-up emails, in order")


class OutreachState(TypedDict):
    lead: dict
    research: str
    initial_email: dict
    followups: list[dict]


def research_node(state: OutreachState) -> dict:
    company = state["lead"]["company"]
    return {"research": research_company(company)}


def draft_initial_node(state: OutreachState, llm) -> dict:
    lead = state["lead"]
    sender = os.getenv("SENDER_NAME") or "[Your Name]"
    system = SystemMessage(content=(
        "You write short, specific first-touch cold outreach emails for a B2B sales team. "
        "Never use generic filler like 'I hope this email finds you well' or 'I wanted to reach out'. "
        "Reference something concrete about the person's company or role. Keep it to 3-5 sentences. "
        "End with a low-friction call to action, like offering a short call, not a hard sell. "
        f"Sign off as {sender}."
    ))
    human = HumanMessage(content=(
        f"Lead: {lead['name']}, {lead['title']} at {lead['company']}.\n"
        f"Extra context on the lead: {lead.get('notes', 'none')}\n"
        f"Company research: {state['research']}\n\n"
        "Write the first outreach email."
    ))
    structured_llm = llm.with_structured_output(EmailDraft)
    result = structured_llm.invoke([system, human])
    return {"initial_email": result.model_dump()}


def draft_followups_node(state: OutreachState, llm) -> dict:
    lead = state["lead"]
    system = SystemMessage(content=(
        "You write short follow-up emails for a B2B sales sequence. Write exactly 2 follow-ups "
        "to be sent if the first email gets no reply, one for day 3 and one for day 7. "
        "Each should be shorter than the original, add a new small piece of value or angle, "
        "not just 'just following up'. The day 7 email should make it easy for the person to say "
        "no and close the loop, not just repeat the ask a third time."
    ))
    human = HumanMessage(content=(
        f"Lead: {lead['name']}, {lead['title']} at {lead['company']}.\n"
        f"Company research: {state['research']}\n"
        f"Original email sent:\nSubject: {state['initial_email']['subject']}\n"
        f"Body: {state['initial_email']['body']}\n\n"
        "Write the 2 follow-up emails."
    ))
    structured_llm = llm.with_structured_output(FollowupSequence)
    result = structured_llm.invoke([system, human])
    return {"followups": [f.model_dump() for f in result.followups]}


def build_graph(model: str | None = None, llm=None):
    llm = llm or get_llm(model)

    graph = StateGraph(OutreachState)
    graph.add_node("research", research_node)
    graph.add_node("draft_initial", lambda state: draft_initial_node(state, llm))
    graph.add_node("draft_followups", lambda state: draft_followups_node(state, llm))

    graph.add_edge(START, "research")
    graph.add_edge("research", "draft_initial")
    graph.add_edge("draft_initial", "draft_followups")
    graph.add_edge("draft_followups", END)

    return graph.compile()


def run_for_lead(lead: dict, model: str | None = None) -> dict:
    graph = build_graph(model)
    return graph.invoke({"lead": lead})
