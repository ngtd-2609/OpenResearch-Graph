from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    async def send_action_link(self, recipient: str, subject: str, url: str) -> None:
        if settings.email_backend == "console":
            logger.info("Development email recipient=%s subject=%s action_url=%s", recipient, subject, url)
            return
        message = EmailMessage()
        message["From"] = settings.email_from
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(
            "OpenResearch Graph received an account action request.\n\n"
            f"Open this one-time link: {url}\n\n"
            "If you did not request this action, ignore this email."
        )
        await asyncio.to_thread(self._send_smtp, message)

    @staticmethod
    def _send_smtp(message: EmailMessage) -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
