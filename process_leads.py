"""Run the outreach agent over a batch of leads, with a human approval step
before anything gets sent.

Run:
    python process_leads.py

Add --send to actually send approved emails over SMTP (requires SMTP_* env
vars). Without --send, everything runs in dry-run mode, drafts get written
to output/outreach_drafts.csv and nothing is emailed, which is the safe
default and the right mode for a demo or a first look at the drafts.
"""

import argparse
import csv
from pathlib import Path

from dotenv import load_dotenv

from agent.email_sender import send_email
from agent.outreach import run_for_lead

load_dotenv()

LEADS_FILE = Path(__file__).parent / "data" / "leads.csv"
OUTPUT_FILE = Path(__file__).parent / "output" / "outreach_drafts.csv"


def load_leads() -> list[dict]:
    with open(LEADS_FILE, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def print_draft(lead: dict, result: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"Lead: {lead['name']} ({lead['title']} at {lead['company']})")
    print(f"{'-' * 60}")
    print(f"Research used: {result['research'][:200]}...")
    print("\nINITIAL EMAIL")
    print(f"Subject: {result['initial_email']['subject']}")
    print(result["initial_email"]["body"])

    for i, followup in enumerate(result["followups"], start=1):
        print(f"\nFOLLOW-UP {i}")
        print(f"Subject: {followup['subject']}")
        print(followup["body"])
    print(f"{'=' * 60}")


def build_row(lead: dict, result: dict, approved: bool, send_status: str) -> dict:
    row = {
        "name": lead["name"],
        "company": lead["company"],
        "email": lead["email"],
        "approved": approved,
        "send_status": send_status,
        "initial_subject": result["initial_email"]["subject"],
        "initial_body": result["initial_email"]["body"],
    }
    # The model is asked for exactly two follow-ups, but don't crash the
    # whole batch if it ever returns fewer.
    followups = result.get("followups") or []
    for i in (1, 2):
        followup = followups[i - 1] if len(followups) >= i else {}
        row[f"followup_{i}_subject"] = followup.get("subject", "")
        row[f"followup_{i}_body"] = followup.get("body", "")
    return row


def save_rows(rows: list[dict]) -> None:
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Actually send approved emails over SMTP")
    args = parser.parse_args()

    leads = load_leads()
    if not leads:
        print(f"No leads found in {LEADS_FILE.name}. Add some rows and try again.")
        return

    rows_out = []
    print(f"Loaded {len(leads)} leads from {LEADS_FILE.name}\n")

    try:
        for lead in leads:
            result = run_for_lead(lead)
            print_draft(lead, result)

            choice = input("\nApprove this outreach? [y]es / [s]kip: ").strip().lower()
            approved = choice == "y"

            send_status = "not sent (not approved)"
            if approved:
                dry_run = not args.send
                if args.send:
                    confirm = input(f"Really send a real email to {lead['email']}? [y/n]: ").strip().lower()
                    dry_run = confirm != "y"
                try:
                    send_status = send_email(
                        to=lead["email"],
                        subject=result["initial_email"]["subject"],
                        body=result["initial_email"]["body"],
                        dry_run=dry_run,
                    )
                except Exception as exc:
                    send_status = f"send failed: {exc}"
                print(send_status)

            rows_out.append(build_row(lead, result, approved, send_status))
    except KeyboardInterrupt:
        print("\nStopped early, saving what's been reviewed so far.")
    finally:
        if rows_out:
            save_rows(rows_out)
            print(f"\nSaved {len(rows_out)} results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
