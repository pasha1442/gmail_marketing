import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from email_parser import parse_email_content, save_images
from gmail_fetch import fetch_emails_from_sender

def html_to_markdown(html_content):
    """Convert HTML to basic Markdown"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Replace common HTML tags with Markdown
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        tag.replace_with(f"{'#' * level} {tag.get_text()}\n\n")
    
    for tag in soup.find_all('strong'):
        tag.replace_with(f"**{tag.get_text()}**")
    
    for tag in soup.find_all('em'):
        tag.replace_with(f"*{tag.get_text()}*")
    
    for tag in soup.find_all('a'):
        href = tag.get('href', '')
        text = tag.get_text()
        tag.replace_with(f"[{text}]({href})")
    
    for tag in soup.find_all('br'):
        tag.replace_with('\n')
    
    for tag in soup.find_all('p'):
        tag.replace_with(f"{tag.get_text()}\n\n")
    
    return soup.get_text()

def save_email_as_markdown(parsed_email, output_dir="emails"):
    """Save email content as Markdown file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create safe filename from subject
    subject = parsed_email['subject']
    safe_filename = re.sub(r'[^\w\s-]', '', subject).strip()
    safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
    filename = f"{safe_filename}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Save images and get paths
    image_paths = []
    if parsed_email['images']:
        image_dir = os.path.join(output_dir, "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        for i, image in enumerate(parsed_email['images']):
            img_filename = image['filename'] or f"image_{i}.jpg"
            img_path = os.path.join(image_dir, img_filename)
            
            with open(img_path, 'wb') as f:
                f.write(image['data'])
            
            image_paths.append(f"images/{img_filename}")
    
    # Create Markdown content
    markdown_content = f"""# {parsed_email['subject']}

**From:** {parsed_email['from']}  
**Date:** {parsed_email['date']}

---

"""
    
    # Add text content
    if parsed_email['text_body']:
        markdown_content += parsed_email['text_body']
    elif parsed_email['html_body']:
        markdown_content += html_to_markdown(parsed_email['html_body'])
    
    # Add images
    if image_paths:
        markdown_content += "\n\n## Images\n\n"
        for img_path in image_paths:
            markdown_content += f"![Image]({img_path})\n\n"
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filepath

if __name__ == "__main__":
    # Fetch and convert email to Markdown
    emails = fetch_emails_from_sender("newsfeed@on.com", limit=1)
    
    if emails:
        parsed = parse_email_content(emails[0]['raw_email'])
        md_path = save_email_as_markdown(parsed)
        
        print(f"✅ Email saved as Markdown: {md_path}")
        print(f"📧 Subject: {parsed['subject']}")
        print(f"🖼️  Images: {len(parsed['images'])} found")
        
        # Show preview
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n📄 Preview (first 300 chars):")
            print(content[:300] + "..." if len(content) > 300 else content)
    else:
        print("❌ No emails found")