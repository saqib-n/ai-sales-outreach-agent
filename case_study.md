# AI Sales Outreach Agent

## Portfolio entry

Researches each lead, writes a personalised cold email that references something specific about their company, and drafts a two-step follow-up sequence. Nothing sends without a human approving it, and the default mode is dry-run. Built as a LangGraph pipeline with Pydantic structured output, so every draft comes back as a clean subject and body rather than text to parse. Falls back to local research data when no search API key is set, so the personalisation is visible in a demo without paying for search first.

**Stack:** Python, LangGraph, LangChain, Pydantic, Tavily, SMTP

---

## The problem with "AI outreach"

Most tools in this space automate templating. Merge a name and a company into a template, send at volume, hope something lands. Prospects have seen thousands of these and delete them on sight.

What actually gets a reply is an email that reads like someone spent two minutes looking at your company before writing. That's slow to do by hand at volume, and it's genuinely a good fit for an LLM with real research behind it, as long as the research is real and the writing avoids the tells.

## What "avoid the tells" meant in practice

The prompt bans "I hope this email finds you well" and "I wanted to reach out" explicitly, because the model reaches for both by default. Three to five sentences. One concrete detail about the company. A low-friction ask rather than a pitch.

The follow-ups each have to add something. "Just circling back" is the phrase that makes a sequence feel automated, and the day 7 email is written to make saying no easy, because a clean no is more valuable than a fourth ignored email.

## The decision I'd defend in a client call

This does not auto-send, and it does not automate LinkedIn.

Cold email goes out under a real person's name. A hallucinated claim about someone's company, or a tone that doesn't match the brand, is a real cost to the sender's reputation. So the default is dry-run, drafts print to the terminal and land in a CSV, and putting anything in a stranger's inbox takes an explicit `--send` flag plus a per-lead confirmation.

LinkedIn is out for a different reason. There's no official send API and automating it risks getting the client's account restricted. So the tool drafts the message and a human sends it. I'd rather explain that limit up front than explain a banned sales account afterwards.

## The research fallback

Requiring a paid search key before anything works is bad for a demo, and a lot of clients want to see something run before handing over credentials. Without a Tavily key the agent reads from a local file of company notes instead, and the difference is visible, the Acme Robotics email genuinely differs from the Northwind Traders one.

With a key set, it does real web search and the same pipeline runs unchanged.

## Biggest gap

The follow-ups are written up front but nothing schedules or sends them. A real deployment needs a scheduler plus reply detection, so follow-up 2 goes out on day 3 only to leads who haven't responded. That's the first thing I'd build for a paying client and it's honestly the difference between this being a drafting tool and a working sequence.

## My part

The pipeline design, the LangGraph implementation with structured output, the prompt work that got the emails to stop sounding generated, and the approval and dry-run layer around sending.
