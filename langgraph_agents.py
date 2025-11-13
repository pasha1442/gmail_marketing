import os
import json
import base64
from typing import TypedDict, Annotated
from datetime import datetime
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

class EmailDNAState(TypedDict):
    email_content: str
    images_dir: str
    content_analysis: dict
    image_analysis: dict
    final_dna: dict
    status: str

class EmailDNAAgents:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0.3
        )
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0.2,
            max_tokens=1000
        )
    
    def content_agent(self, state: EmailDNAState) -> EmailDNAState:
        """Agent to extract RAW data + analyze email content"""
        print("📄 Content Agent: Extracting raw data + analyzing...")
        
        with open(state["email_content"], 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Extract raw data first
        raw_data = self._extract_raw_content(raw_content)
        
        # Then analyze
        prompt = f"""
        Analyze this email content and extract COMPLETE marketing DNA. Return ONLY valid JSON:

        {raw_content}

        {{
            "subject_line_dna": {{
                "text": "actual subject line",
                "length": 45,
                "emotional_triggers": ["urgency", "curiosity", "fear", "desire"],
                "power_words": ["exclusive", "limited", "free", "new"],
                "personalization_level": "none/basic/advanced",
                "urgency_indicators": ["today", "limited", "expires"],
                "predicted_open_rate": "high/medium/low"
            }},
            "content_structure_dna": {{
                "word_count": 200,
                "paragraph_count": 4,
                "opening_hook_type": "question/benefit/story/urgency",
                "value_propositions": ["specific benefits listed"],
                "social_proof_elements": ["testimonials", "customer_count", "reviews"],
                "scarcity_signals": ["limited_quantity", "time_sensitive"],
                "closing_technique": "urgency/benefit/question"
            }},
            "cta_dna": {{
                "primary_cta": {{
                    "text": "Shop Now",
                    "action_type": "purchase/signup/learn_more",
                    "urgency_level": "high/medium/low",
                    "position": "top/middle/bottom/multiple"
                }},
                "secondary_ctas": ["Learn More", "Browse Products"],
                "cta_count": 2,
                "cta_strategy": "single_focus/multiple_options"
            }},
            "psychological_triggers": {{
                "urgency_score": 7,
                "scarcity_indicators": ["few_left", "limited_time"],
                "authority_markers": ["expert_endorsement", "certifications"],
                "reciprocity_elements": ["free_gift", "valuable_content"],
                "social_proof_strength": "high/medium/low"
            }},
            "offer_dna": {{
                "discount_type": "percentage/dollar/bogo/none",
                "discount_value": 25,
                "offer_presentation": "crossed_out_price/badge/highlight",
                "bonus_items": ["free_shipping", "gift"],
                "guarantee_type": "money_back/satisfaction/warranty"
            }},
            "brand_voice_dna": {{
                "tone": "friendly/professional/urgent/casual",
                "personality_traits": ["helpful", "authoritative", "playful"],
                "emotional_temperature": "warm/neutral/cool",
                "formality_level": "casual/business_casual/formal",
                "reading_level": "elementary/middle_school/high_school/college"
            }}
        }}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content_text = response.content.strip()
            if content_text.startswith('```json'):
                content_text = content_text[7:]
            if content_text.startswith('```'):
                content_text = content_text[3:]
            if content_text.endswith('```'):
                content_text = content_text[:-3]
            
            content_analysis = json.loads(content_text.strip())
        except Exception as e:
            print(f"Content analysis error: {e}")
            content_analysis = {
                "subject_line_dna": {"text": "Welcome", "length": 7, "emotional_triggers": ["welcome"], "power_words": [], "personalization_level": "basic", "urgency_indicators": [], "predicted_open_rate": "medium"},
                "content_structure_dna": {"word_count": 200, "paragraph_count": 3, "opening_hook_type": "benefit", "value_propositions": ["membership benefits"], "social_proof_elements": [], "scarcity_signals": [], "closing_technique": "benefit"},
                "cta_dna": {"primary_cta": {"text": "Get Started", "action_type": "signup", "urgency_level": "low", "position": "bottom"}, "secondary_ctas": [], "cta_count": 1, "cta_strategy": "single_focus"},
                "psychological_triggers": {"urgency_score": 3, "scarcity_indicators": [], "authority_markers": [], "reciprocity_elements": [], "social_proof_strength": "low"},
                "offer_dna": {"discount_type": "none", "discount_value": 0, "offer_presentation": "none", "bonus_items": [], "guarantee_type": "none"},
                "brand_voice_dna": {"tone": "friendly", "personality_traits": ["helpful"], "emotional_temperature": "warm", "formality_level": "casual", "reading_level": "middle_school"}
            }
        
        # Combine raw data + analysis
        state["content_analysis"] = {
            "raw_data": raw_data,
            "analysis": content_analysis
        }
        state["status"] = "content_analyzed"
        return state
    
    def _extract_raw_content(self, content: str) -> dict:
        """Extract raw email data from markdown format"""
        import re
        
        # Extract subject line from markdown header
        subject_match = re.search(r'^#\s*(.+)', content, re.MULTILINE)
        subject = subject_match.group(1).strip() if subject_match else "No subject found"
        
        # Extract sender info
        sender_match = re.search(r'\*\*From:\*\*\s*(.+)', content)
        sender = sender_match.group(1).strip() if sender_match else "Unknown sender"
        
        # Extract date
        date_match = re.search(r'\*\*Date:\*\*\s*(.+)', content)
        date = date_match.group(1).strip() if date_match else "Unknown date"
        
        # Extract all links with better parsing
        links = []
        
        # Markdown image links: [![text](image)](url)
        image_links = re.findall(r'\[!\[([^\]]+)\]\([^\)]+\)\]\(([^\)]+)\)', content)
        for text, url in image_links:
            links.append({
                "url": url,
                "anchor_text": text,
                "link_type": "image_link",
                "position": "body"
            })
        
        # Regular markdown links: [text](url)
        markdown_links = re.findall(r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)', content)
        for text, url in markdown_links:
            # Skip if it's part of an image link
            if not url.startswith('images/'):
                links.append({
                    "url": url,
                    "anchor_text": text,
                    "link_type": "text_link",
                    "position": "body"
                })
        
        # Image references: ![alt](image_path)
        images = re.findall(r'!\[([^\]]+)\]\(([^\)]+)\)', content)
        image_refs = []
        for alt_text, img_path in images:
            image_refs.append({
                "alt_text": alt_text,
                "image_path": img_path,
                "image_type": "embedded_image"
            })
        
        # Extract main content sections
        sections = []
        
        # Benefits section
        benefits_match = re.search(r'## Your benefits\.\.\.(.+?)(?=##|---|\n\n©)', content, re.DOTALL)
        if benefits_match:
            benefits_text = benefits_match.group(1).strip()
            # Extract individual benefits
            benefit_links = re.findall(r'\*\*\[([^\]]+)\]\([^\)]+\)\*\*', benefits_text)
            sections.append({
                "section_type": "benefits",
                "content": benefits_text,
                "benefits_list": benefit_links
            })
        
        # Main message section
        main_msg_match = re.search(r'## Enjoy your unlocked benefits(.+?)## Your benefits', content, re.DOTALL)
        if main_msg_match:
            main_message = main_msg_match.group(1).strip()
            sections.append({
                "section_type": "main_message",
                "content": main_message
            })
        
        # Footer section
        footer_match = re.search(r'\*\*Follow us:\*\*(.+?)(?=---|\n\nYou are receiving)', content, re.DOTALL)
        if footer_match:
            footer_content = footer_match.group(1).strip()
            social_links = re.findall(r'\[([^\]]+)\]\([^\)]+\)', footer_content)
            sections.append({
                "section_type": "footer_social",
                "content": footer_content,
                "social_platforms": social_links
            })
        
        # Clean text without markdown
        clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Remove links, keep text
        clean_text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', clean_text)  # Remove images
        clean_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', clean_text)  # Remove bold
        clean_text = re.sub(r'#+\s*', '', clean_text)  # Remove headers
        clean_text = re.sub(r'---+', '', clean_text)  # Remove dividers
        clean_text = '\n'.join(line.strip() for line in clean_text.split('\n') if line.strip())
        
        return {
            "original_email": {
                "subject_line": subject,
                "sender": sender,
                "date": date,
                "full_body_text": clean_text,
                "raw_markdown": content
            },
            "extracted_links": links,
            "image_references": image_refs,
            "content_sections": sections,
            "content_stats": {
                "total_characters": len(content),
                "total_words": len(clean_text.split()),
                "total_links": len(links),
                "total_images": len(image_refs),
                "format_type": "markdown"
            }
        }
    
    def analyze_single_image(self, image_path: str, filename: str) -> dict:
        """Analyze a single image using OpenAI Vision API"""
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = f"""
            Analyze this email marketing image in COMPLETE detail. Describe EXACTLY what you see + marketing analysis. Return ONLY valid JSON:
            {{
                "filename": "{filename}",
                "raw_visual_description": {{
                    "scene_description": "Detailed description of what you see: people, objects, setting, actions",
                    "people_details": "Age, gender, clothing, pose, expression, activity of any people",
                    "objects_present": ["smartphone", "clothing", "background_elements"],
                    "text_in_image": "EXACT text visible in the image",
                    "colors_observed": ["specific colors you can see"],
                    "setting_context": "indoor/outdoor/studio/lifestyle/product_shot",
                    "mood_atmosphere": "energetic/calm/professional/casual/luxury"
                }},
                "visual_elements": {{
                    "image_type": "logo/hero/product/banner/cta_button/icon/lifestyle",
                    "dominant_colors": ["#FF6B35", "#2E86AB", "#F5F5F5"],
                    "color_psychology": ["energetic", "trustworthy", "clean"],
                    "text_content": "any visible text or CTA",
                    "design_style": "modern/classic/minimalist/bold/elegant",
                    "layout_pattern": "centered/left_aligned/grid/asymmetric"
                }},
                "brand_dna": {{
                    "professionalism_score": 8,
                    "brand_consistency": "high/medium/low",
                    "visual_appeal": "excellent/good/average/poor",
                    "target_demographic": "young_adults/professionals/families/luxury",
                    "brand_personality": ["innovative", "trustworthy", "playful"]
                }},
                "marketing_psychology": {{
                    "cta_visibility": "high/medium/low",
                    "emotional_impact": "strong/moderate/weak",
                    "attention_grabbing": "high/medium/low",
                    "urgency_visual_cues": ["countdown", "red_colors", "bold_text"],
                    "trust_signals": ["badges", "testimonials", "guarantees"],
                    "conversion_elements": ["product_focus", "benefit_highlight", "social_proof"]
                }},
                "technical_analysis": {{
                    "resolution": "high/medium/low",
                    "mobile_optimization": true,
                    "composition_quality": "excellent/good/average/poor",
                    "color_harmony": "excellent/good/average/poor",
                    "text_readability": "high/medium/low"
                }},
                "competitive_insights": {{
                    "innovation_level": "cutting_edge/standard/basic",
                    "industry_trends": ["minimalism", "bold_colors", "mobile_first"],
                    "differentiation_factors": ["unique_layout", "color_scheme", "typography"]
                }},
                "recommendations": ["specific actionable improvements"]
            }}
            """
            
            response = self.vision_llm.invoke([
                HumanMessage(content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ])
            ])
            
            # Clean the response content to extract JSON
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Try to parse JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If still fails, try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise ValueError(f"No valid JSON found in response: {content[:200]}...")
            
        except Exception as e:
            print(f"Error analyzing {filename}: {str(e)}")
            # Print the actual response for debugging
            try:
                if 'response' in locals():
                    print(f"Raw response: {response.content[:300]}...")
            except:
                pass
            
            return {
                "filename": filename,
                "error": str(e),
                "visual_elements": {"image_type": "unknown", "dominant_colors": [], "text_content": "", "design_style": "unknown"},
                "brand_analysis": {"professionalism_score": 5, "brand_consistency": "unknown", "visual_appeal": "unknown"},
                "marketing_effectiveness": {"cta_visibility": "unknown", "emotional_impact": "unknown", "attention_grabbing": "unknown", "mobile_friendly": False},
                "technical_quality": {"resolution": "unknown", "composition": "unknown", "color_harmony": "unknown"},
                "recommendations": ["Unable to analyze - check image format and accessibility"]
            }
    
    def image_agent(self, state: EmailDNAState) -> EmailDNAState:
        """Agent to analyze email images using OpenAI Vision API"""
        print("🖼️ Image Agent: Analyzing visual elements with AI Vision...")
        
        images_dir = state["images_dir"]
        image_analyses = []
        
        # Get all image files
        if os.path.exists(images_dir):
            image_files = [f for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
            
            print(f"Found {len(image_files)} images to analyze...")
            
            for img_file in image_files:
                print(f"  Analyzing: {img_file}")
                img_path = os.path.join(images_dir, img_file)
                analysis = self.analyze_single_image(img_path, img_file)
                image_analyses.append(analysis)
        else:
            print(f"Images directory not found: {images_dir}")
        
        # Aggregate analysis
        total_images = len(image_analyses)
        avg_professionalism = sum([img.get('brand_analysis', {}).get('professionalism_score', 5) 
                                  for img in image_analyses]) / max(total_images, 1)
        
        all_colors = []
        image_types = []
        for img in image_analyses:
            colors = img.get('visual_elements', {}).get('dominant_colors', [])
            all_colors.extend(colors)
            img_type = img.get('visual_elements', {}).get('image_type', 'unknown')
            if img_type not in image_types:
                image_types.append(img_type)
        
        image_analysis = {
            "individual_analyses": image_analyses,
            "summary": {
                "total_images": total_images,
                "image_types": image_types,
                "common_colors": list(set(all_colors))[:10],  # Top 10 unique colors
                "avg_professionalism_score": round(avg_professionalism, 1)
            },
            "overall_assessment": {
                "visual_consistency": "high" if avg_professionalism >= 7 else "medium" if avg_professionalism >= 5 else "low",
                "brand_strength": "strong" if avg_professionalism >= 8 else "moderate" if avg_professionalism >= 6 else "weak",
                "marketing_impact": "high" if total_images > 0 and avg_professionalism >= 7 else "medium"
            }
        }
        
        state["image_analysis"] = image_analysis
        state["status"] = "images_analyzed"
        return state
    
    def dna_synthesizer(self, state: EmailDNAState) -> EmailDNAState:
        """Agent to synthesize comprehensive email DNA"""
        print("🧬 DNA Synthesizer: Creating comprehensive email DNA...")
        
        content = state["content_analysis"]
        visuals = state["image_analysis"]
        
        # Calculate overall effectiveness scores
        content_score = self._calculate_content_score(content)
        visual_score = visuals.get("summary", {}).get("avg_professionalism_score", 5)
        overall_score = round((content_score + visual_score) / 2, 1)
        
        # Determine email type from content
        email_type = self._determine_email_type(content)
        
        # Generate competitive insights
        competitive_insights = self._generate_competitive_insights(content, visuals)
        
        # Generate actionable recommendations
        recommendations = self._generate_recommendations(content, visuals, overall_score)
        
        final_dna = {
            "email_dna": {
                "meta_data": {
                    "email_type": email_type,
                    "overall_effectiveness_score": overall_score,
                    "content_score": content_score,
                    "visual_score": visual_score,
                    "analysis_timestamp": datetime.now().isoformat()
                },
                "raw_data": {
                    "original_email": content.get("raw_data", {}).get("original_email", {}),
                    "extracted_links": content.get("raw_data", {}).get("extracted_links", []),
                    "image_references": content.get("raw_data", {}).get("image_references", []),
                    "content_sections": content.get("raw_data", {}).get("content_sections", []),
                    "content_stats": content.get("raw_data", {}).get("content_stats", {}),
                    "image_descriptions": self._extract_image_descriptions(visuals)
                },
                "content_dna": content.get("analysis", {}),
                "visual_dna": visuals,
                "competitive_intelligence": competitive_insights,
                "actionable_recommendations": recommendations,
                "replication_blueprint": self._create_replication_blueprint(content.get("analysis", {}), visuals)
            }
        }
        
        state["final_dna"] = final_dna
        state["status"] = "complete"
        return state
    
    def _calculate_content_score(self, content: dict) -> float:
        """Calculate content effectiveness score"""
        score = 5.0  # Base score
        
        # Get analysis part if nested
        analysis = content.get("analysis", content)
        
        # Subject line factors
        subject = analysis.get("subject_line_dna", {})
        if subject.get("predicted_open_rate") == "high":
            score += 1.5
        elif subject.get("predicted_open_rate") == "medium":
            score += 0.5
        
        # Psychological triggers
        triggers = analysis.get("psychological_triggers", {})
        urgency_score = triggers.get("urgency_score", 0)
        score += min(urgency_score / 10 * 2, 2)  # Max 2 points for urgency
        
        # CTA effectiveness
        cta = analysis.get("cta_dna", {})
        if cta.get("primary_cta", {}).get("urgency_level") == "high":
            score += 1
        
        # Offer strength
        offer = analysis.get("offer_dna", {})
        if offer.get("discount_type") != "none":
            score += 0.5
        
        return min(round(score, 1), 10.0)
    
    def _determine_email_type(self, content: dict) -> str:
        """Determine email type from content analysis"""
        analysis = content.get("analysis", content)
        cta = analysis.get("cta_dna", {})
        offer = analysis.get("offer_dna", {})
        
        if offer.get("discount_type") != "none":
            return "promotional_sale"
        elif cta.get("primary_cta", {}).get("action_type") == "signup":
            return "welcome_onboarding"
        elif "product" in str(content).lower():
            return "product_launch"
        else:
            return "newsletter_engagement"
    
    def _generate_competitive_insights(self, content: dict, visuals: dict) -> dict:
        """Generate competitive intelligence insights"""
        strengths = []
        opportunities = []
        advantages = []
        
        # Analyze strengths
        if content.get("psychological_triggers", {}).get("urgency_score", 0) >= 7:
            strengths.append("Strong urgency creation")
        if visuals.get("summary", {}).get("avg_professionalism_score", 0) >= 8:
            strengths.append("Professional visual design")
        if len(content.get("cta_dna", {}).get("secondary_ctas", [])) > 0:
            strengths.append("Multiple engagement options")
        
        # Identify opportunities
        if content.get("psychological_triggers", {}).get("social_proof_strength") == "low":
            opportunities.append("Add customer testimonials and reviews")
        if content.get("offer_dna", {}).get("guarantee_type") == "none":
            opportunities.append("Include risk-reversal guarantee")
        
        # Competitive advantages
        if content.get("brand_voice_dna", {}).get("emotional_temperature") == "warm":
            advantages.append("Emotionally engaging brand voice")
        
        return {
            "strengths": strengths or ["Professional presentation"],
            "opportunities": opportunities or ["Optimize conversion elements"],
            "competitive_advantages": advantages or ["Clear communication"]
        }
    
    def _generate_recommendations(self, content: dict, visuals: dict, score: float) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        if score < 7:
            recommendations.append("Increase urgency and scarcity elements")
        
        if content.get("cta_dna", {}).get("cta_count", 0) < 2:
            recommendations.append("Add secondary CTA options")
        
        if content.get("psychological_triggers", {}).get("social_proof_strength") != "high":
            recommendations.append("Include customer testimonials and social proof")
        
        if visuals.get("summary", {}).get("avg_professionalism_score", 0) < 8:
            recommendations.append("Enhance visual design quality")
        
        return recommendations or ["Optimize for mobile viewing", "A/B test subject lines"]
    
    def _extract_image_descriptions(self, visuals: dict) -> list:
        """Extract raw visual descriptions from image analysis"""
        descriptions = []
        for img in visuals.get("individual_analyses", []):
            if "raw_visual_description" in img:
                descriptions.append({
                    "filename": img.get("filename", "unknown"),
                    "visual_description": img.get("raw_visual_description", {}).get("scene_description", "No description"),
                    "people_details": img.get("raw_visual_description", {}).get("people_details", "No people detected"),
                    "text_in_image": img.get("raw_visual_description", {}).get("text_in_image", "No text detected"),
                    "objects_detected": img.get("raw_visual_description", {}).get("objects_present", []),
                    "scene_context": img.get("raw_visual_description", {}).get("setting_context", "unknown")
                })
        return descriptions
    
    def _create_replication_blueprint(self, content: dict, visuals: dict) -> dict:
        """Create blueprint for replicating successful elements"""
        return {
            "subject_line_formula": {
                "structure": content.get("subject_line_dna", {}).get("text", "Unknown"),
                "key_triggers": content.get("subject_line_dna", {}).get("emotional_triggers", []),
                "optimal_length": content.get("subject_line_dna", {}).get("length", 50)
            },
            "content_structure": {
                "opening_hook": content.get("content_structure_dna", {}).get("opening_hook_type", "benefit"),
                "cta_strategy": content.get("cta_dna", {}).get("cta_strategy", "single_focus"),
                "closing_technique": content.get("content_structure_dna", {}).get("closing_technique", "benefit")
            },
            "visual_formula": {
                "color_palette": visuals.get("summary", {}).get("common_colors", [])[:3],
                "design_style": "modern",
                "image_types": visuals.get("summary", {}).get("image_types", [])
            }
        }

def create_email_dna_workflow():
    """Create LangGraph workflow for email DNA generation"""
    agents = EmailDNAAgents()
    
    workflow = StateGraph(EmailDNAState)
    
    # Add nodes
    workflow.add_node("content_agent", agents.content_agent)
    workflow.add_node("image_agent", agents.image_agent)
    workflow.add_node("dna_synthesizer", agents.dna_synthesizer)
    
    # Define edges
    workflow.set_entry_point("content_agent")
    workflow.add_edge("content_agent", "image_agent")
    workflow.add_edge("image_agent", "dna_synthesizer")
    workflow.add_edge("dna_synthesizer", END)
    
    return workflow.compile()

def run_email_dna_analysis():
    """Run the complete email DNA analysis workflow"""
    print("🚀 Starting LangGraph Email DNA Analysis")
    print("=" * 50)
    
    # Initialize state
    initial_state = {
        "email_content": "/home/auriga/Documents/MarseerEngineering/emails/Youre-in-Welcome-to-the-Community.md",
        "images_dir": "/home/auriga/Documents/MarseerEngineering/images",
        "content_analysis": {},
        "image_analysis": {},
        "final_dna": {},
        "status": "starting"
    }
    
    # Create and run workflow
    workflow = create_email_dna_workflow()
    result = workflow.invoke(initial_state)
    
    # Save results
    with open("email_dna_langgraph.json", "w") as f:
        json.dump(result["final_dna"], f, indent=2)
    
    print("\n" + "=" * 50)
    print("🎯 LangGraph Email DNA Analysis Complete!")
    print("📊 Results saved to: email_dna_langgraph.json")
    
    return result

if __name__ == "__main__":
    run_email_dna_analysis()