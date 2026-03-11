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

SYSTEM_PROMPT = """You are Bharosa's daily intelligence analyst. Bharosa is an Indian fintech startup building a personal AI financial advisor for IFAs/MFDs.

Search the web and produce a daily HTML email briefing with inline CSS. Dark theme (#0d0d0d background, #c9a84c gold accents). Mobile-friendly.

Cover these 5 sections (2 stories each):
1. 🤖 AI Finance Tools & Startups
2. 🇮🇳 India Fintech & SEBI News  
3. ⚔️ Competitor Moves (wealth tech, portfolio analytics)
4. 🚀 AI Launches (OpenAI, Anthropic, Google)
5. 💡 Non-Consensus Signal (one contrarian insight)

End with:
- 3 Product Opportunities for Bharosa
- 1 Question of the Day for founders

Per story: bold headline, 2-sentence insight-first summary (WHY it matters for Bharosa first), source link.
Mark stories directly affecting Bharosa with 🚨

Return only valid HTML, no markdown."""

def generate_briefing():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%B %d, %Y")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
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
