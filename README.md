# Instagram Reels Multi-Agent Workflow System

An intelligent, multi-step agentic workflow that automates the creation of Instagram Reels using AI agents.

## 🎯 Features

- **Agent A (Trend & Concept Strategist)**: Generates 3 high-engagement Reel concepts based on your niche
- **Agent B (Scriptwriter & Prompt Engineer)**: Creates optimized scripts and visual prompts
- **Agent C (Media Generator)**: Generates high-quality images using AI
- **Agent D (Voice & Video Assembler)**: Produces voiceovers and assembles final video

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg installed on your system
- API keys for:
  - **Azure OpenAI** (recommended) or **OpenAI**
  - **ElevenLabs** (for voiceover)
  - **Replicate** (optional, for alternative image generation)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd InstaAgent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

**Streamlit UI:**
```bash
streamlit run app.py
```

**CLI Interface:**
```bash
python cli.py
```

## 📁 Project Structure

```
InstaAgent/
├── agents/
│   ├── __init__.py
│   ├── concept_strategist.py      # Agent A
│   ├── scriptwriter.py            # Agent B
│   ├── media_generator.py         # Agent C
│   └── video_assembler.py         # Agent D
├── orchestrator/
│   ├── __init__.py
│   ├── workflow.py                # LangGraph workflow
│   └── state_manager.py           # State persistence
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py
│   ├── api_clients.py
│   └── video_utils.py
├── state/                          # Saved workflow states
├── output/                         # Generated videos
├── app.py                          # Streamlit UI
├── cli.py                          # CLI interface
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 API Keys Required

- **Azure OpenAI** (Recommended) or **OpenAI**: 
  - For GPT-4 (concepts, scripts) and DALL-E 3 (images)
  - See [Azure Setup Guide](cursor_doc/AZURE_SETUP.md) for detailed instructions
- **ElevenLabs**: For high-quality voiceover generation
- **Replicate** (Optional): Alternative image generation provider

## 🎬 Workflow

1. **Input**: User provides niche/keywords
2. **Agent A**: Generates 3 concepts → User selects one
3. **Agent B**: Creates script + sequential image prompts
4. **Agent C**: Generates images for each prompt
5. **Agent D**: Creates voiceover + assembles final video

## 📝 State Management

The system automatically saves state at each step, allowing you to:
- Resume interrupted workflows
- Refine specific stages without losing progress
- Review and modify intermediate outputs

## 🛠️ Configuration

Edit `.env` to customize:
- API models and providers
- Video resolution and quality
- Rate limiting parameters
- Voice selection

## 📄 License

MIT License
