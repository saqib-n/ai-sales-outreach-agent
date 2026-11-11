"""Sends the approved email over SMTP, or just logs it if dry_run is True.

Defaults to dry_run=True on purpose, this is an outbound sales tool and
accidentally emailing real people while testing is exactly the kind of
mistake that should require an explicit opt-in, not a config file you
might forget about.
"""

import os
import smtplib
from email.mime.text import MIMEText

REQUIRED_SETTINGS = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD")


def send_email(to: str, subject: str, body: str, dry_run: bool = True) -> str:
    if dry_run:
        return f"[DRY RUN] Would send to {to} | Subject: {subject}"

    missing = [name for name in REQUIRED_SETTINGS if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Can't send email, set {', '.join(missing)} in .env first.")

    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT") or "587")
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    # An empty SMTP_FROM_ADDRESS in .env should fall back too, not send a
    # message with a blank From header.
    from_address = os.getenv("SMTP_FROM_ADDRESS") or username

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, [to], message.as_string())

    return f"Sent to {to} | Subject: {subject}"
