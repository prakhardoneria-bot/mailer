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
HTML_FILE = "mail.html"
PROGRESS_FILE = "progress.txt"
WA_LINK = "https://chat.whatsapp.com/LIn9ooUhHvjKWUm5s5tnDL"

def get_last_checkpoint():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except:
            return 0
    return 0

def save_checkpoint(index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

def send_batch():
    try:
        # Reads data.txt using whitespace/tab as separator and assigns column names
        df = pd.read_csv(DATA_FILE, sep=r'\s+', header=None, names=['Email', 'Role'])
        df['Email'] = df['Email'].astype(str).str.strip()
        
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            template = Template(f.read())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    start_index = get_last_checkpoint()
    batch_size = 150 
    end_index = min(start_index + batch_size, len(df))
    
    if start_index >= len(df):
        print("All emails sent!")
        return

    print(f"Processing batch: {start_index} to {end_index}")

    for index in range(start_index, end_index):
        row = df.iloc[index]
        recipient_email = row['Email']
        
        # Extracts name from email (e.g., 'aakritikpro' from 'aakritikpro@gmail.com')
        # This acts as a fallback since the text file doesn't have names
        first_name = recipient_email.split('@')[0].capitalize()

        try:
            html_body = template.render(name=first_name)
            msg = EmailMessage()
            msg['Subject'] = f"The code is calling, {first_name}! Are you in? 👨‍💻"
            msg['From'] = f"GFG-IEC Student Chapter <{GMAIL_USER}>"
            msg['To'] = recipient_email
            
            msg.set_content(f"Hi {first_name}, GFG is now at IEC! Join us: {WA_LINK}")
            msg.add_alternative(html_body, subtype='html')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ [{index + 1}] Sent to {recipient_email}")
            save_checkpoint(index + 1)
            
            if index < end_index - 1:
                # Randomized delay to mimic natural sending
                time.sleep(random.randint(60, 90))

        except Exception as e:
            print(f"Error at index {index}: {e}")
            time.sleep(10)

if __name__ == "__main__":
    send_batch()
