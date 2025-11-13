from email_parser import parse_email_content
from gmail_fetch import fetch_emails_from_sender
from bs4 import BeautifulSoup
import requests

def extract_text_from_html(html_content):
    """Extract clean text from HTML"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')

    extract_images_from_email(soup)

    return soup.get_text(strip=True)


def extract_images_from_email(soup):
    if not soup:
        return
    for i, img in enumerate(soup.find_all("img")):
        url = img.get("src")
        if url and url.startswith("http"):
            data = requests.get(url).content
            with open(f"images/image_{i+1}.jpg", "wb") as f:
                f.write(data)

if __name__ == "__main__":
    # Test with one email
    emails = fetch_emails_from_sender("newsfeed@on.com", limit=1)
    
    if emails:
        parsed = parse_email_content(emails[0]['raw_email'])
        
        print("=== STEP 2 TEST RESULTS ===")
        print(f"✅ Subject: {parsed['subject']}")
        print(f"✅ From: {parsed['from']}")
        print(f"✅ HTML Content: {len(parsed['html_body'])} characters")
        print(f"✅ Text Content: {len(parsed['text_body'])} characters")
        print(f"✅ Images: {len(parsed['images'])} found")
        
        # Extract readable text from HTML
        if parsed['html_body']:
            clean_text = extract_text_from_html(parsed['html_body'])
            print(f"\n📄 Clean Text Preview (first 300 chars):")
            print(clean_text[:300] + "..." if len(clean_text) > 300 else clean_text)
        
        print(f"\n🎯 Step 2 Complete: Email content successfully parsed!")
    else:
        print("❌ No emails found")