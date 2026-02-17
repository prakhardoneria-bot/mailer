import pandas as pd
import smtplib
import time
import random
import os
import sys
from email.message import EmailMessage
from jinja2 import Template

# --- CONFIGURATION ---
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
DATA_FILE = "data.txt"
HTML_FILE = "hack.html"
PROGRESS_FILE = "progress.txt"
WA_LINK = "https://chat.whatsapp.com/LIn9ooUhHvjKWUm5s5tnDL"

def get_last_checkpoint():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except Exception:
            return 0
    return 0

def save_checkpoint(index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

def send_batch():
    try:
        # Reads data.txt: [Email] [Role/Name]
        df = pd.read_csv(DATA_FILE, sep=r'\s+', header=None, names=['Email', 'Role'])
        df['Email'] = df['Email'].astype(str).str.strip()
        
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            template = Template(f.read())
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)

    start_index = get_last_checkpoint()
    
    # --- AUTOMATION STRATEGY ---
    # Sending ~40 emails per run. With a cron job every 2 hours, 
    # you stay well under Gmail's 500/day limit for personal accounts.
    EMAILS_PER_RUN = 40 
    
    if start_index >= len(df):
        print("All emails have been sent! Resetting progress to 0 for next campaign.")
        save_checkpoint(0)
        return

    end_index = min(start_index + EMAILS_PER_RUN, len(df))
    print(f"Starting run: Sending from index {start_index} to {end_index}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            
            for i in range(start_index, end_index):
                recipient_email = df.iloc[i]['Email']
                
                # Personalization: Use "IECian" or name from data.txt
                html_body = template.render(name="IECian") 
                
                msg = EmailMessage()
                msg['Subject'] = "Register for Hack-A-Geek Event and win FREE GOODIES👨‍💻"
                msg['From'] = f"GFG-IEC Student Chapter"
                msg['To'] = recipient_email 
                
                msg.set_content(f"Hi IECian, GFG is now at IEC! Join us: {WA_LINK}")
                msg.add_alternative(html_body, subtype='html')

                server.send_message(msg)
                print(f"✅ [{i+1}/{len(df)}] Sent to: {recipient_email}")
                
                # Update progress after every successful email
                save_checkpoint(i + 1)
                
                # Random delay (15-45s) to avoid spam detection
                time.sleep(random.randint(15, 45))

    except Exception as e:
        print(f"Connection error or limit reached: {e}")

if __name__ == "__main__":
    send_batch()
