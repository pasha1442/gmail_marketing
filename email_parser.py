import email
from email.header import decode_header
import base64
import os
from gmail_fetch import fetch_emails_from_sender

def parse_email_content(raw_email):
    """Parse raw email and extract structured content"""
    msg = email.message_from_bytes(raw_email)
    
    # Decode subject
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()
    
    parsed_data = {
        'subject': subject,
        'from': msg.get("From"),
        'date': msg.get("Date"),
        'text_body': '',
        'html_body': '',
        'images': []
    }
    
    # Extract content from multipart message
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Extract text content
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True)
                if body:
                    parsed_data['text_body'] = body.decode('utf-8', errors='ignore')
            
            # Extract HTML content
            elif content_type == "text/html" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True)
                if body:
                    parsed_data['html_body'] = body.decode('utf-8', errors='ignore')
            
            # Extract images
            elif content_type.startswith('image/'):
                filename = part.get_filename()
                if filename:
                    # Decode filename
                    filename = decode_header(filename)[0][0]
                    if isinstance(filename, bytes):
                        filename = filename.decode()
                    
                    image_data = part.get_payload(decode=True)
                    parsed_data['images'].append({
                        'filename': filename,
                        'content_type': content_type,
                        'size': len(image_data),
                        'data': image_data
                    })
    else:
        # Single part message
        content_type = msg.get_content_type()
        body = msg.get_payload(decode=True)
        if body:
            if content_type == "text/plain":
                parsed_data['text_body'] = body.decode('utf-8', errors='ignore')
            elif content_type == "text/html":
                parsed_data['html_body'] = body.decode('utf-8', errors='ignore')
    
    return parsed_data

def save_images(parsed_email, output_dir="images"):
    """Save extracted images to disk"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_images = []
    for i, image in enumerate(parsed_email['images']):
        filename = image['filename'] or f"image_{i}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image['data'])
        
        saved_images.append(filepath)
    
    return saved_images

if __name__ == "__main__":
    # Fetch and parse emails
    emails = fetch_emails_from_sender("newsfeed@on.com", limit=1)
    
    if emails:
        email_obj = emails[0]
        parsed = parse_email_content(email_obj['raw_email'])
        
        print("=== PARSED EMAIL CONTENT ===")
        print(f"Subject: {parsed['subject']}")
        print(f"From: {parsed['from']}")
        print(f"Date: {parsed['date']}")
        print(f"\nText Body ({len(parsed['text_body'])} chars):")
        print(parsed['text_body'][:200] + "..." if len(parsed['text_body']) > 200 else parsed['text_body'])
        print(f"\nHTML Body ({len(parsed['html_body'])} chars):")
        print(parsed['html_body'][:200] + "..." if len(parsed['html_body']) > 200 else parsed['html_body'])
        print(f"\nImages found: {len(parsed['images'])}")
        
        if parsed['images']:
            saved_paths = save_images(parsed)
            print(f"Images saved to: {saved_paths}")
    else:
        print("No emails found")