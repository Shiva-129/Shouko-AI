import os
import time
import html
import httpx
from core.config import settings
import logging
logger = logging.getLogger("services.email_service")

class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.sandbox_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sandbox_emails")
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def compile_digest_html(self, user_name: str, recommendations: list[dict]) -> str:
        rows = ""
        for rec in recommendations:
            category = html.escape(rec.get("category", "Computer Science"))
            match_score = rec.get("match_score", 90)
            title = html.escape(rec.get("title", "Untitled Ingested Paper"))
            abstract_preview = html.escape((rec.get("abstract") or "No abstract available.")[:280])
            url = html.escape(rec.get("url", "#"))
            rows += f"""
            <tr>
                <td style="padding: 20px; border-bottom: 1px solid #1e293b; background-color: #0b1329;">
                    <div style="font-size: 10px; font-weight: 700; color: #3b82f6; text-transform: uppercase; margin-bottom: 6px;">
                        {category} • {match_score}% Matching
                    </div>
                    <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700; color: #ffffff;">
                        {title}
                    </h3>
                    <p style="margin: 0 0 12px 0; font-size: 13px; color: #94a3b8; line-height: 1.5;">
                        {abstract_preview}...
                    </p>
                    <div style="display: flex; gap: 8px;">
                        <a href="{url}" style="display: inline-block; font-size: 12px; font-weight: 600; color: #3b82f6; text-decoration: none; border: 1px solid #1e293b; padding: 6px 12px; border-radius: 6px; background-color: #0f172a;">
                            View Workspace
                        </a>
                    </div>
                </td>
            </tr>
            """
        safe_user = html.escape(user_name)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Shouko-AI Daily Digest</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #020617; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 40px auto; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);">
                <tr>
                    <td style="padding: 30px; text-align: center; background-color: #0f172a; border-bottom: 1px solid #1e293b;">
                        <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                            Shouko <span style="color: #3b82f6;">Digest</span>
                        </h1>
                        <p style="margin: 6px 0 0 0; font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">
                            DAILY RESEARCH INTELLIGENCE
                        </p>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 24px; background-color: #090d1f; border-bottom: 1px solid #1e293b;">
                        <p style="margin: 0; font-size: 14px; color: #cbd5e1; line-height: 1.6;">
                            Hello <strong>{safe_user}</strong>,<br>
                            Here are today's top curated academic recommendations, dynamically matched against your active research profile:
                        </p>
                    </td>
                </tr>
                {rows}
                <tr>
                    <td style="padding: 24px; text-align: center; background-color: #0f172a; font-size: 11px; color: #475569;">
                        <p style="margin: 0 0 4px 0;">Sent automatically by your Shouko-AI Discovery Agent.</p>
                        <p style="margin: 0;">© 2026 Shouko-AI. All rights reserved.</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html_template

    async def send_digest(self, to_email: str, user_name: str, recommendations: list[dict]) -> bool:
        """
        Sends the compiled daily digest. Fallback to sandbox if Resend API key is not present.
        """
        html_content = self.compile_digest_html(user_name, recommendations)

        # 1. Attempt live API delivery if API key is present and not running in test mode
        if self.api_key and settings.ENVIRONMENT != "test":
            logger.info(f"[EmailService] Initiating Resend API transmission to {to_email}...")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "from": f"Shouko-AI <{settings.RESEND_FROM_EMAIL}>",
                            "to": to_email,
                            "subject": "Your Daily Shouko-AI Academic Digest 🤖",
                            "html": html_content
                        },
                        timeout=10.0
                    )
                    if response.status_code in (200, 201):
                        logger.info(f"[EmailService] Resend dispatch success! Response: {response.json()}")
                        return True
                    if settings.ENVIRONMENT == "development":
                        logger.info(f"[EmailService] Resend API error (Code {response.status_code}): {response.text}. Falling back to sandbox...")
                    else:
                        raise RuntimeError(f"Resend API error (Code {response.status_code}): {response.text}")
                except Exception as e:
                    if settings.ENVIRONMENT == "development":
                        logger.info(f"[EmailService] Resend client transmission failure: {e}. Falling back to sandbox...")
                    else:
                        logger.info(f"[EmailService] Resend client transmission failure: {e}")
                        raise RuntimeError(f"Failed to transmit email via Resend API: {e}") from e

        # 2. Local sandbox fallback (dev/test without API key)
        timestamp = int(time.time())
        sandbox_file = os.path.join(self.sandbox_dir, f"digest_email_{timestamp}.html")
        with open(sandbox_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"[EmailService] Sandboxed digest written: {sandbox_file}")
        return True

    def compile_welcome_html(self, user_name: str) -> str:
        safe_user = html.escape(user_name)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Shouko-AI</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #020617; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 40px auto; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);">
                <tr>
                    <td style="padding: 30px; text-align: center; background-color: #0f172a; border-bottom: 1px solid #1e293b;">
                        <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                            Welcome to <span style="color: #a3e635;">Shouko-AI</span>
                        </h1>
                        <p style="margin: 6px 0 0 0; font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">
                            YOUR AGENTIC RESEARCH WORKSPACE
                        </p>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 30px; background-color: #090d1f; border-bottom: 1px solid #1e293b;">
                        <p style="margin: 0 0 16px 0; font-size: 15px; color: #ffffff; font-weight: 600;">
                            Hello {safe_user},
                        </p>
                        <p style="margin: 0 0 20px 0; font-size: 14px; color: #cbd5e1; line-height: 1.6;">
                            We're thrilled to have you join Shouko-AI! Our mission is to accelerate scientific discovery by giving researchers and developers a unified agentic workspace to read, digest, and query academic publications.
                        </p>
                        <p style="margin: 0 0 16px 0; font-size: 14px; color: #ffffff; font-weight: 600;">
                            Here's what you can do next:
                        </p>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 24px;">
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b;">
                                     <div style="font-size: 13px; font-weight: bold; color: #a3e635; margin-bottom: 4px;">1. Configure Research Interests</div>
                                    <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">Head to Settings > Interest Profile to set topics, categories, and keywords for your personalized daily discovery digests.</div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #1e293b;">
                                    <div style="font-size: 13px; font-weight: bold; color: #a3e635; margin-bottom: 4px;">2. Upload Publications</div>
                                    <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">Ingest ArXiv IDs or upload PDFs directly into your library to automatically generate structured research wikis (artifacts).</div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0;">
                                    <div style="font-size: 13px; font-weight: bold; color: #a3e635; margin-bottom: 4px;">3. Chat with Context</div>
                                    <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">Start conversation threads directly with any ingested paper. Our pgvector-powered RAG agent provides answers complete with source highlights.</div>
                                </td>
                            </tr>
                        </table>
                        <div style="text-align: center; margin-top: 30px; margin-bottom: 10px;">
                            <a href="https://shouko-ai.app/dashboard" style="display: inline-block; font-size: 13px; font-weight: 700; color: #0d0d0d; text-decoration: none; padding: 12px 24px; border-radius: 8px; background-color: #a3e635;">
                                Go to Workspace
                            </a>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 24px; text-align: center; background-color: #0f172a; font-size: 11px; color: #475569;">
                        <p style="margin: 0 0 4px 0;">You received this welcome email because you signed up for Shouko-AI.</p>
                        <p style="margin: 0;">© 2026 Shouko-AI. All rights reserved.</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html_template

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Sends the welcome onboarding email. Fallback to sandbox if Resend API key is not present.
        """
        html_content = self.compile_welcome_html(user_name)

        # 1. Attempt live API delivery if API key is present and not running in test mode
        if self.api_key and settings.ENVIRONMENT != "test":
            logger.info(f"[EmailService] Initiating Welcome Email Resend transmission to {to_email}...")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "from": f"Shouko-AI <{settings.RESEND_FROM_EMAIL}>",
                            "to": to_email,
                            "subject": "Welcome to Shouko-AI! 🤖",
                            "html": html_content
                        },
                        timeout=10.0
                    )
                    if response.status_code in (200, 201):
                        logger.info(f"[EmailService] Welcome email dispatch success! Response: {response.json()}")
                        return True
                    if settings.ENVIRONMENT == "development":
                        logger.info(f"[EmailService] Resend API error (Code {response.status_code}): {response.text}. Falling back to sandbox...")
                    else:
                        raise RuntimeError(f"Resend API error (Code {response.status_code}): {response.text}")
                except Exception as e:
                    if settings.ENVIRONMENT == "development":
                        logger.info(f"[EmailService] Resend client transmission failure: {e}. Falling back to sandbox...")
                    else:
                        logger.info(f"[EmailService] Resend client transmission failure: {e}")
                        raise RuntimeError(f"Failed to transmit welcome email via Resend API: {e}") from e

        # 2. Local sandbox fallback (dev/test without API key)
        timestamp = int(time.time())
        sandbox_file = os.path.join(self.sandbox_dir, f"welcome_email_{timestamp}.html")
        with open(sandbox_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"[EmailService] Sandboxed welcome email written: {sandbox_file}")
        return True
