import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

def connect_gmail():
    """Connect to Gmail IMAP server"""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    email_user = os.getenv('GMAIL_USER')
    email_pass = os.getenv('GMAIL_APP_PASSWORD')
    
    if not email_user or not email_pass:
        raise ValueError("Gmail credentials not found in environment variables")
    
    mail.login(email_user, email_pass)
    return mail

def fetch_emails_from_sender(sender_email="newsfeed@on.com", limit=10):
    """Fetch emails from specific sender"""
    mail = connect_gmail()
    mail.select("inbox")
    
    # Search for emails from specific sender
    status, messages = mail.search(None, f'FROM "{sender_email}"')
    email_ids = messages[0].split()
    
    emails = []
    for email_id in email_ids[-limit:]:  # Get latest emails
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        # Decode subject
        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        
        email_obj = {
            'id': email_id.decode(),
            'subject': subject,
            'from': email_message.get("From"),
            'date': email_message.get("Date"),
            'raw_email': raw_email
        }
        emails.append(email_obj)
    
    mail.close()
    mail.logout()
    return emails

if __name__ == "__main__":
    try:
        emails = fetch_emails_from_sender()
        print(f"Fetched {len(emails)} emails from newsfeed@on.com:")
        for email_obj in emails:
            print(f"- {email_obj['subject']}")
    except Exception as e:
        print(f"Error: {e}")