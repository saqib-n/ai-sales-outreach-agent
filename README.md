<div align="center">

<h1>AI Sales Outreach Agent</h1>

<p><b>Researches each lead, writes a cold email that mentions something real about their company, drafts two follow-ups, and then waits for a person to approve it.</b></p>

<p>
  <a href="https://github.com/saqib-n/ai-sales-outreach-agent/actions/workflows/tests.yml"><img src="https://github.com/saqib-n/ai-sales-outreach-agent/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python: 3.12+">
  <img src="https://img.shields.io/badge/LangGraph-1.x-1C3C3C" alt="LangGraph: 1.x">
  <img src="https://img.shields.io/badge/email-SMTP-D14836?logo=gmail&logoColor=white" alt="email: SMTP">
  <img src="https://img.shields.io/badge/models-OpenAI%20%7C%20Claude%20%7C%20Gemini-444444" alt="models: OpenAI | Claude | Gemini">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2E7D32" alt="license: MIT"></a>
</p>

<p>
  <a href="#what-it-does">What it does</a> &nbsp;|&nbsp;
  <a href="#how-it-works">How it works</a> &nbsp;|&nbsp;
  <a href="#sample-run">Sample run</a> &nbsp;|&nbsp;
  <a href="#quick-start">Quick start</a> &nbsp;|&nbsp;
  <a href="#configuration">Configuration</a> &nbsp;|&nbsp;
  <a href="#roadmap">Roadmap</a>
</p>

</div>

<br>

<h2>See it in action</h2>

<p align="center"><img src="demo/demo.gif" alt="Campaign screen: the agent researches each prospect, writes a three-email sequence, and waits for a person to approve it" width="100%"></p>

<p align="center"><sub>Recorded in the built-in campaign screen from a real run on Google Gemini (<code>gemini-3.5-flash-lite</code>) on 14 November 2026. Nothing is scripted. Only the time spent waiting for the model is fast-forwarded, and the real response times are shown on screen. <a href="demo/demo.mp4">Download the MP4</a>.</sub></p>

<p>Run <code>python app.py</code> and it opens a campaign screen where you watch the agent research each prospect and write the three emails, then approve or skip each one (approval is a dry run). It is the same agent code as the command line version, with a screen on top.</p>

<h2>The problem</h2>

<p>Most AI outreach tools are mail merge with extra steps. A name and a company go into a template and the email goes out at volume. Prospects have seen thousands of these and delete them on sight.</p>

<p>What gets replies is an email that reads like someone spent two minutes looking at the company first. That is slow to do by hand, and it is a good fit for an AI model, as long as the research is real and the writing avoids the usual tells.</p>

<h2>What it does</h2>

<table>
  <tr><th align="left">Capability</th><th align="left">What that means in practice</th></tr>
  <tr><td><b>Lead research</b></td><td>Looks up each company with Tavily, or reads local notes when no search key is set, so the personalisation shows in a demo before you pay for anything.</td></tr>
  <tr><td><b>A first email that sounds human</b></td><td>Three to five sentences, one specific detail about the company and a low-pressure ask. Openers like "I hope this email finds you well" are banned in the prompt.</td></tr>
  <tr><td><b>Two follow-ups</b></td><td>Day 3 and day 7. Each one has to add something new, and the last one makes it easy to say no.</td></tr>
  <tr><td><b>Human approval</b></td><td>You review every lead's emails in the terminal and approve or skip each one.</td></tr>
  <tr><td><b>Safe by default</b></td><td>Dry run unless you pass <code>--send</code>, and even then it asks again before each real email.</td></tr>
  <tr><td><b>Spreadsheet export</b></td><td>Every draft lands in <code>output/outreach_drafts.csv</code>. Progress is saved even if you stop halfway with Ctrl+C.</td></tr>
</table>

<h2>How it works</h2>

<pre>
lead from CSV --&gt; research company --&gt; write first email --&gt; write 2 follow-ups
                                                                    |
                         you approve or skip  &lt;---------------------+
                                |
                    dry run (default) or --send with a second confirmation
</pre>

<p>A short LangGraph pipeline runs the same three steps for every lead: research, first email, follow-ups. Each draft comes back through a Pydantic model, so you always get a clean subject line and body.</p>

<p>Sending uses plain SMTP, so it works with Gmail, Outlook or any mail provider. Set <code>SENDER_NAME</code> and every email is signed with your name.</p>

<h2>Decisions I made on purpose</h2>

<h3>It doesn't send on its own</h3>

<p>Cold email goes out under a real person's name. A wrong claim about someone's company, or a tone that doesn't fit the brand, costs the sender's reputation. So the default is a dry run, and a real send takes an explicit flag plus a confirmation for each lead.</p>

<h3>No LinkedIn automation</h3>

<p>LinkedIn has no official API for sending messages, and automating it puts the account at risk of being restricted. The agent drafts the message and a person sends it. I would rather explain that limit to a client up front than explain a banned sales account afterwards.</p>

<h2>Sample run</h2>

<p>A real run on Google Gemini, one of the four demo leads:</p>

<pre>
Lead: Maria Gonzalez (Head of Operations at Acme Robotics)
------------------------------------------------------------
INITIAL EMAIL
Subject: Fulfillment ops at Acme Robotics
I noticed Acme Robotics is actively expanding into the Midwest and building out
your fulfillment operations team. As you scale hardware delivery, keeping
warehouse fulfillment times down is likely a top priority for your group. ...
Would you be open to a brief 10-minute call next week to see if this aligns
with your goals?

FOLLOW-UP 1
Subject: Quick resource for Acme's Midwest expansion
...
FOLLOW-UP 2
Subject: Closing the loop re: Acme ops workflow
Hi Maria, I am guessing optimizing fulfillment timelines during your Midwest
rollout isn't a top priority right now. If the timing is off, no problem at
all. Should I close the loop for now, or check back in next quarter?
============================================================
Approve this outreach? [y]es / [s]kip:
</pre>

<h2>Quick start</h2>

<p>You need Python 3.12 or newer and an API key from OpenAI, Anthropic or Google Gemini.</p>

<pre>
pip install -r requirements.txt
cp .env.example .env        # on Windows: copy .env.example .env
# open .env and paste your API key
python app.py               # opens the campaign screen at http://localhost:8000
python process_leads.py            # dry run, nothing is sent
python process_leads.py --send     # real sending, asks again per lead
</pre>

<p>Leads come from <code>data/leads.csv</code>. Swap in your own list with the same columns.</p>

<h2>Configuration</h2>

<p>Everything is set in <code>.env</code>. Copy <code>.env.example</code> to start.</p>

<table>
  <tr><th align="left">Variable</th><th align="left">Required</th><th align="left">Purpose</th></tr>
  <tr><td><code>LLM_MODEL</code></td><td>Yes</td><td>Which model to use, as <code>provider:model</code>. Default <code>openai:gpt-5.5</code>. Also works with <code>anthropic:claude-opus-5-5</code> or <code>google_genai:gemini-3.5-flash</code>.</td></tr>
  <tr><td><code>OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY</code></td><td>One of them</td><td>The key for whichever provider you picked.</td></tr>
  <tr><td><code>TAVILY_API_KEY</code></td><td>No</td><td>Live company research. Without it the agent reads <code>data/company_notes.json</code>.</td></tr>
  <tr><td><code>SENDER_NAME</code></td><td>No</td><td>Your name for the email sign-off.</td></tr>
  <tr><td><code>SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_ADDRESS</code></td><td>Only with --send</td><td>Mail server details for real sending. For Gmail, use an app password.</td></tr>
</table>

<h2>Project structure</h2>

<pre>
ai-sales-outreach-agent/
  .env.example            # copy to .env and add your key
  case_study.md           # longer write-up of the design
  process_leads.py        # runs the batch with the approval prompt
  app.py                # browser campaign screen, the same agent with a UI
  README.md
  requirements.txt        # dependencies
  agent/
    email_sender.py       # SMTP sending
    llm.py                # picks the model from LLM_MODEL
    outreach.py           # the LangGraph pipeline and prompts
    research.py           # Tavily lookup with the local fallback
  data/
    company_notes.json    # offline research notes for the sample companies
    leads.csv             # four sample leads
  demo/                   # recording of a live run (GIF, MP4 and a screenshot)
  tests/                  # pytest suite, runs without any API key
  web/
    index.html          # the campaign screen, one file, no build step
</pre>

<h2>Built with</h2>

<p>Python &nbsp;&middot;&nbsp; LangGraph &nbsp;&middot;&nbsp; LangChain &nbsp;&middot;&nbsp; Pydantic &nbsp;&middot;&nbsp; Tavily &nbsp;&middot;&nbsp; SMTP &nbsp;&middot;&nbsp; OpenAI / Anthropic / Gemini</p>

<h2>Tests</h2>

<pre>
pip install -r requirements-dev.txt
pytest
</pre>

<p>Six tests cover the research fallback, the dry-run default, missing mail settings, the email signature and the CSV export, plus the browser screen and its API. None of the tests call a model or need an API key, so they run on GitHub Actions on every push. The badge at the top shows the latest result.</p>

<h2>Roadmap</h2>

<p>What I would build next if a client took this into production:</p>
<ul>
  <li>A scheduler with reply detection, so follow-ups only go to leads who haven't answered. This is the first thing I would build for a client.</li>
  <li>Pulling leads straight from HubSpot, Pipedrive or another CRM instead of a CSV</li>
  <li>Daily sending limits and warm-up for better deliverability at higher volume</li>
</ul>

<h2>More from this series</h2>

<p>Nine production-minded AI agents, each solving one business problem properly.</p>

<table>
  <tr><td><a href="https://github.com/saqib-n/ai-research-report-agent"><b>Research Report Agent</b></a></td><td>Researches a topic, notices its own gaps, and writes a report with a source for every claim.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/ecommerce-automation-agent"><b>E-commerce Order and Inventory Agent</b></a></td><td>Shopify order, stock and returns assistant, plus a monitor that warns you before stock runs out.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/email-triage-agent"><b>Email Triage Agent</b></a></td><td>Sorts an inbox into four buckets and gives each one a different level of autonomy.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/lead-qualification-crm-agent"><b>Lead Qualification Agent</b></a></td><td>Scores inbound leads against your own rubric and pushes the good ones to HubSpot.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/multi-agent-customer-support"><b>Multi-Agent Customer Support</b></a></td><td>A router plus specialist agents for orders, refunds, FAQs and human handoff.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/rag-knowledge-base-agent"><b>RAG Knowledge Base Agent</b></a></td><td>Answers questions from your own documents and names the source for every answer.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/recruiting-screening-agent"><b>Resume Screening Agent</b></a></td><td>Ranks resumes against a job description with evidence, and guards against common bias.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/whatsapp-support-agent"><b>WhatsApp Support Agent</b></a></td><td>A WhatsApp Cloud API agent that checks orders, answers FAQs and escalates to a person.</td></tr>
</table>

<h2>Work with me</h2>

<p>I'm Saqib Nawaz, founder of WolfXense AI. I build AI agents and automations for businesses, with Python, LangChain, LangGraph and n8n, and connect them to the tools teams already use, like CRMs, Shopify, Slack, email and WhatsApp.</p>

<p>If your sales team wants personalised outreach without losing control over what goes out, I can connect this to your CRM, your mailbox and your own tone of voice.</p>

<p><a href="https://www.upwork.com/freelancers/~01de008504a38baf28"><b>Hire me on Upwork</b></a> &nbsp;|&nbsp; <a href="https://github.com/saqib-n"><b>More of my work on GitHub</b></a></p>

<hr>

<p><sub>Released under the <a href="LICENSE">MIT License</a>. A longer write-up of the design is in <a href="case_study.md">case_study.md</a>.</sub></p>
