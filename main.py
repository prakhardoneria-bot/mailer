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
        # Reads data.txt using whitespace/tab as separator
        df = pd.read_csv(DATA_FILE, sep=r'\s+', header=None, names=['Email', 'Role'])
        df['Email'] = df['Email'].astype(str).str.strip()
        
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            template = Template(f.read())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    start_index = get_last_checkpoint()
    
    # --- STRATEGY CONFIGURATION ---
    EMAILS_TO_SEND = 150       # Number of actual emails to send per session
    BCC_PER_EMAIL = 50         # Number of recipients per email in BCC
    
    total_recipients_this_run = EMAILS_TO_SEND * BCC_PER_EMAIL
    end_index = min(start_index + total_recipients_this_run, len(df))
    
    if start_index >= len(df):
        print("All emails from the data file have been sent!")
        return

    print(f"Starting run: Target {total_recipients_this_run} people via {EMAILS_TO_SEND} emails.")

    current_pos = start_index
    emails_sent_count = 0

    while current_pos < end_index and emails_sent_count < EMAILS_TO_SEND:
        # Get the next chunk of recipients for the BCC field
        batch_end = min(current_pos + BCC_PER_EMAIL, end_index)
        recipients = df.iloc[current_pos:batch_end]['Email'].tolist()
        
        if not recipients:
            break

        try:
            # Updated name field to "IECian" as requested
            html_body = template.render(name="IECian") 
            msg = EmailMessage()
            msg['Subject'] = "The code is calling, IECian! Are you in? 👨‍💻"
            msg['From'] = f"GFG-IEC Student Chapter <{GMAIL_USER}>"
            
            # Send 'To' yourself and 'Bcc' the recipients
            msg['To'] = GMAIL_USER 
            msg['Bcc'] = ", ".join(recipients)
            
            msg.set_content(f"Hi IECian, GFG is now at IEC! Join us: {WA_LINK}")
            msg.add_alternative(html_body, subtype='html')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            emails_sent_count += 1
            print(f"✅ Email {emails_sent_count}/{EMAILS_TO_SEND} sent. (Recipients {current_pos} to {batch_end})")
            
            current_pos = batch_end
            save_checkpoint(current_pos) # Updates progress.txt
            
            # Randomized delay to mimic natural sending
            time.sleep(random.randint(30, 60))

        except Exception as e:
            print(f"Error at recipient index {current_pos}: {e}")
            time.sleep(20)

    print(f"Finished! Total people reached this session: {current_pos - start_index}")

if __name__ == "__main__":
    send_batch()
