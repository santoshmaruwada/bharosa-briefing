import anthropic
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- CONFIG ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]

SYSTEM_PROMPT = """You are Bharosa's daily strategic intelligence analyst. Bharosa is an Indian fintech startup building a personal AI financial advisor — the "operating system for personal finance." Their edge is a financial calculation engine for messy personal data (mutual funds, stocks, taxes, goals, loans). They target IFAs/MFDs in India.

Your job is NOT to summarize news. Surface SIGNALS — what people are thinking, struggling with, building, debating around AI + personal finance.

Produce a daily briefing in clean HTML format suitable for email. Use inline CSS only.

Structure:
1. TODAY'S INSIGHT — 1 bold non-consensus observation for founders (highlighted box)
2. 🤖 AI Finance Tools & Startups — 3 stories
3. ⚔️ Competitor Moves — 3 stories  
4. 🇮🇳 India Market & Regulation — 3 stories
5. 🚀 General AI Launches — 3 stories
6. 📡 User Signals (Reddit/Communities) — 3 stories
7. 💡 Non-Consensus Signals — 2 stories
8. 🎯 Product Opportunities for Bharosa — 3 bullets
9. 🧠 Question of the Day — 1 sharp strategic question

For each story: bold headline, 2-sentence insight-first summary, source link.
Flag stories that directly threaten or help Bharosa with 🚨 BHAROSA ALERT.

Design: dark professional email, background #0d0d0d, gold accents #c9a84c, readable on mobile.
Insight-first means: explain WHY it matters for Bharosa before describing what happened."""

def generate_briefing():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%B %d, %Y")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"Generate today's Bharosa intelligence briefing. Today is {today}. Search for latest news. Return only HTML."
        }]
    )
    
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text
    
    return html_content

def send_email(html_content):
    today = datetime.now().strftime("%B %d, %Y")
    subject = f"Bharosa Briefing — {today}"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL
    
    msg.attach(MIMEText(html_content, "html"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())
    
    print(f"Briefing sent to {TO_EMAIL}")

if __name__ == "__main__":
    print("Generating briefing...")
    html = generate_briefing()
    print("Sending email...")
    send_email(html)
    print("Done!")
