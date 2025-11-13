#!/usr/bin/env python3
"""
Complete Email Processing Pipeline
Fetch → Parse → Markdown → LangGraph Analysis
"""

from gmail_fetch import fetch_emails_from_sender
from email_parser import parse_email_content, save_images
from email_to_markdown import save_email_as_markdown
from test_parser import extract_text_from_html

try:
    from langgraph_agents import run_email_dna_analysis
except ImportError:
    print("⚠️  langgraph_agents.py not found - skipping LangGraph step")
    run_email_dna_analysis = None

def main():
    """Run complete email processing pipeline"""
    print("🚀 Starting Complete Email Processing Pipeline")
    print("=" * 50)
    
    try:
        # Step 1: Fetch emails
        print("📧 Step 1: Fetching emails...")
        emails = fetch_emails_from_sender("newsfeed@on.com", limit=1)
        
        if not emails:
            print("❌ No emails found")
            return
        
        print(f"✅ Fetched {len(emails)} emails")
        
        # Step 2: Parse email content
        print("\n🔍 Step 2: Parsing email content...")
        parsed = parse_email_content(emails[0]['raw_email'])
        
        print(f"✅ Subject: {parsed['subject']}")
        print(f"✅ Images: {len(parsed['images'])} found")
        
        # Step 3: Save images
        if parsed['images']:
            print("\n🖼️  Step 3: Saving images...")
            image_paths = save_images(parsed)
            print(f"✅ Images saved: {len(image_paths)} files")
        
        # Step 4: Convert to Markdown
        print("\n📝 Step 4: Converting to Markdown...")
        md_path = save_email_as_markdown(parsed)
        print(f"✅ Markdown saved: {md_path}")
        
        # Step 5: Extract clean text
        print("\n📄 Step 5: Extracting clean text...")
        if parsed['html_body']:
            clean_text = extract_text_from_html(parsed['html_body'])
            print(f"✅ Clean text extracted: {len(clean_text)} characters")
        
        # Step 6: LangGraph Analysis
        if run_email_dna_analysis:
            print("\n🧬 Step 6: Running LangGraph DNA analysis...")
            try:
                result = run_email_dna_analysis()
                print("✅ LangGraph analysis completed")
                print(f"📊 Results saved to output files")
            except Exception as e:
                print(f"❌ LangGraph error: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Complete Pipeline Finished!")
        print(f"📧 Email: {parsed['subject']}")
        print(f"📝 Markdown: {md_path}")
        print(f"🖼️  Images: {len(parsed['images'])} saved")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")

if __name__ == "__main__":
    main()