import pandas as pd
import smtplib
import time
import random
import os
import sys
from email.message import EmailMessage
from jinja2 import Template

# --- CONFIGURATION ---
# These are pulled from GitHub Repository Secrets for security
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# File paths in your repository
CSV_FILE = "community.csv"
HTML_FILE = "mail.html"
PROGRESS_FILE = "progress.txt"

# WhatsApp link for the plain-text fallback
WA_LINK = "https://chat.whatsapp.com/LIn9ooUhHvjKWUm5s5tnDL"

def get_last_checkpoint():
    """Reads the last sent index from progress.txt."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except (ValueError, FileNotFoundError):
            return 0
    return 0

def save_checkpoint(index):
    """Saves the current index to progress.txt."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

def send_batch():
    # 1. Load the CSV and HTML Template
    try:
        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip()
        
        if not os.path.exists(HTML_FILE):
            print(f"CRITICAL: {HTML_FILE} not found!")
            sys.exit(1)
            
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            template = Template(f.read())
    except Exception as e:
        print(f"CRITICAL: Setup error: {e}")
        sys.exit(1)

    # 2. Determine Batch Range
    start_index = get_last_checkpoint()
    batch_size = 150 
    end_index = min(start_index + batch_size, len(df))
    
    if start_index >= len(df):
        print("🎉 All emails in the list have been sent!")
        return

    print(f"🚀 Starting session: Processing indices {start_index} to {end_index-1}")

    # 3. Execution Loop
    for index in range(start_index, end_index):
        row = df.iloc[index]
        
        # Adjust 'Name' and 'Email' to match your CSV headers exactly
        full_name = str(row['Name']).strip()
        first_name = full_name.split()[0] if full_name else "Student"
        recipient_email = str(row['Email']).strip()

        try:
            # Render personalized HTML
            html_body = template.render(name=first_name)

            msg = EmailMessage()
            msg['Subject'] = f"The code is calling, {first_name}! Are you in? 👨‍💻"
            msg['From'] = f"GFG-IEC Student Chapter <{GMAIL_USER}>"
            msg['To'] = recipient_email
            
            # Plain text fallback for safety
            msg.set_content(f"Hi {first_name}, GFG is now at IEC! Join our community: {WA_LINK}")
            msg.add_alternative(html_body, subtype='html')

            # Re-establishing connection per email is safer for long 'sleep' durations
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ [{index + 1}/{len(df)}] Sent to {full_name}")
            
            # Save progress immediately after each success
            save_checkpoint(index + 1)
            
            # 4. Human-like Delay Logic
            if index < end_index - 1:
                wait_time = random.randint(60, 90)
                print(f"⏳ Sleeping for {wait_time}s to maintain account safety...")
                time.sleep(wait_time)

        except smtplib.SMTPAuthenticationError:
            print("❌ FATAL: Gmail Login failed. Check your GMAIL_APP_PASSWORD Secret.")
            sys.exit(1)
        except Exception as e:
            print(f"⚠️ Error at index {index} ({full_name}): {e}")
            # Brief pause before attempting next to avoid rapid-fire errors
            time.sleep(10) 

    print(f"\n✅ Session finished. Progress saved at index {end_index}.")

if __name__ == "__main__":
    send_batch()
