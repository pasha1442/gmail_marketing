#!/usr/bin/env python3
"""
LangGraph Email DNA Analysis Runner
"""
import os
from langgraph_agents import run_email_dna_analysis

def main():
    print("🔗 LangGraph Email DNA Analysis System")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Check files exist
    email_path = "/home/auriga/Documents/MarseerEngineering/emails/Youre-in-Welcome-to-the-Community.md"
    images_path = "/home/auriga/Documents/MarseerEngineering/images"
    
    if not os.path.exists(email_path):
        print("❌ Email content not found")
        return
    
    if not os.path.exists(images_path):
        print("❌ Images directory not found")
        return
    
    try:
        result = run_email_dna_analysis()
        print(f"\n✅ Analysis complete!")
        print(f"📈 Overall Score: {result['final_dna']['email_dna']['overall_score']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()