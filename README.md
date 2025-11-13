# Gmail Marketing Intelligence Platform

An AI-powered email marketing analysis platform that extracts the "DNA" of competitor emails to help create better marketing campaigns. This system fetches emails from Gmail, analyzes their content and visual elements using advanced AI, and generates comprehensive insights for marketing optimization.

## 🎯 What We Do

This platform performs **competitive email intelligence** by:

1. **Fetching competitor emails** from Gmail using IMAP
2. **Parsing email content** (HTML, text, images, links)
3. **Converting to structured formats** (Markdown)
4. **AI-powered analysis** using OpenAI GPT-4 Vision
5. **Generating email DNA** - comprehensive marketing insights
6. **Creating replication blueprints** for successful campaigns

## 🤔 Why We Do This

**Problem**: Creating effective email marketing campaigns requires understanding what works in your industry, but manually analyzing competitor emails is time-consuming and subjective.

**Solution**: Our platform automates the analysis of competitor emails to extract actionable marketing intelligence, including:
- Subject line effectiveness patterns
- Content structure strategies
- Visual design elements
- Psychological triggers used
- Call-to-action optimization
- Brand voice characteristics

**Value**: Transform competitor research from hours of manual work into automated, AI-powered insights that directly improve your email marketing performance.

## 🏗️ System Architecture

```
Gmail IMAP → Email Parser → Markdown Converter → AI Analysis → DNA Report
     ↓            ↓              ↓               ↓           ↓
 Raw Emails → Structured → Clean Format → LangGraph → Actionable
              Content                     Agents     Insights
```

## 📁 Project Structure

```
gmail_marketing/
├── main.py                 # Complete pipeline orchestrator
├── gmail_fetch.py          # Gmail IMAP email fetching
├── email_parser.py         # Email content extraction
├── email_to_markdown.py    # HTML to Markdown conversion
├── test_parser.py          # Text extraction utilities
├── langgraph_agents.py     # AI analysis agents (LangGraph)
├── run_langgraph.py        # LangGraph workflow runner
├── requirements.txt        # Python dependencies
├── emails/                 # Processed email storage
│   └── *.md               # Converted email files
├── images/                 # Extracted email images
└── email_dna_langgraph.json # Final analysis results
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Gmail App Password** (for IMAP access)
3. **OpenAI API Key** (for AI analysis)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd gmail_marketing

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Configuration

Create a `.env` file with:

```env
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
OPENAI_API_KEY=your-openai-api-key
```

### Usage

#### Complete Pipeline
```bash
# Run full analysis pipeline
python main.py
```

#### Individual Components
```bash
# Fetch emails only
python gmail_fetch.py

# Parse specific email
python email_parser.py

# Convert to markdown
python email_to_markdown.py

# Run AI analysis
python run_langgraph.py
```

## 🧬 Email DNA Analysis

Our AI system extracts comprehensive "DNA" from emails:

### Content Analysis
- **Subject Line DNA**: Length, triggers, power words, open rate prediction
- **Structure DNA**: Word count, hooks, value propositions, social proof
- **CTA DNA**: Button text, urgency level, positioning strategy
- **Psychological Triggers**: Urgency, scarcity, authority, reciprocity
- **Offer DNA**: Discounts, bonuses, guarantees
- **Brand Voice DNA**: Tone, personality, emotional temperature

### Visual Analysis (AI Vision)
- **Design Elements**: Colors, layout, typography
- **Brand Consistency**: Professional score, visual appeal
- **Marketing Psychology**: CTA visibility, emotional impact
- **Technical Quality**: Resolution, mobile optimization
- **Competitive Insights**: Innovation level, differentiation

### Output Format

```json
{
  "email_dna": {
    "meta_data": {
      "email_type": "promotional_sale",
      "overall_effectiveness_score": 8.2,
      "analysis_timestamp": "2025-01-XX"
    },
    "raw_data": {
      "original_email": {...},
      "extracted_links": [...],
      "image_descriptions": [...]
    },
    "content_dna": {...},
    "visual_dna": {...},
    "competitive_intelligence": {...},
    "actionable_recommendations": [...],
    "replication_blueprint": {...}
  }
}
```

## 🔧 Core Components

### 1. Gmail Fetcher (`gmail_fetch.py`)
- Connects to Gmail via IMAP SSL
- Searches emails by sender
- Extracts raw email data
- Handles authentication securely

### 2. Email Parser (`email_parser.py`)
- Parses multipart email messages
- Extracts text, HTML, and images
- Decodes headers and attachments
- Saves images to disk

### 3. Markdown Converter (`email_to_markdown.py`)
- Converts HTML emails to clean Markdown
- Preserves links and formatting
- Embeds images with proper paths
- Creates readable documentation

### 4. AI Analysis Engine (`langgraph_agents.py`)
- **Content Agent**: Analyzes text and structure
- **Image Agent**: Uses GPT-4 Vision for visual analysis
- **DNA Synthesizer**: Combines insights into actionable intelligence
- **LangGraph Workflow**: Orchestrates multi-agent analysis

## 🎯 Use Cases

1. **Competitive Research**: Analyze competitor email strategies
2. **Campaign Optimization**: Improve your email performance
3. **A/B Testing**: Generate data-driven test variations
4. **Brand Analysis**: Understand industry communication patterns
5. **Training**: Learn from successful email campaigns

## 📊 Sample Analysis Results

**Subject Line Analysis**:
- "☁️ Unlock exclusive gifts and rewards" 
- Length: 35 characters (optimal)
- Triggers: Exclusivity, rewards, visual emoji
- Predicted open rate: High

**Content Strategy**:
- Hook: Personalization request
- Structure: Welcome → Benefits → CTA
- Psychological triggers: Reciprocity, exclusivity
- CTA strategy: Single focus with secondary options

## 🛠️ Technical Stack

- **Python 3.8+**: Core language
- **LangGraph**: Multi-agent AI workflow
- **OpenAI GPT-4**: Content and vision analysis
- **BeautifulSoup**: HTML parsing
- **IMAP**: Gmail integration
- **Markdown**: Content formatting

## 📋 Requirements

```
python-dotenv==1.0.0
beautifulsoup4==4.12.2
requests==2.31.0
langchain-openai==0.2.8
langgraph==0.2.45
langchain-core==0.3.75
langchain==0.3.27
langchain-text-splitters==0.3.11
langchain-google-genai==2.0.10
langchain-community==0.3.11
langsmith==0.1.147
openai==1.54.3
```

## 🔒 Security & Privacy

- Uses Gmail App Passwords (not main password)
- Environment variables for sensitive data
- No email content stored permanently
- Local processing only
- Respects email privacy

## 🚦 Pipeline Status Tracking

The system provides real-time feedback:

```
🚀 Starting Complete Email Processing Pipeline
📧 Step 1: Fetching emails...
🔍 Step 2: Parsing email content...
🖼️  Step 3: Saving images...
📝 Step 4: Converting to Markdown...
📄 Step 5: Extracting clean text...
🧬 Step 6: Running LangGraph DNA analysis...
🎯 Complete Pipeline Finished!
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check existing issues
2. Create detailed bug reports
3. Include error logs and environment details

---

**Transform your email marketing with AI-powered competitive intelligence.** 🚀 
