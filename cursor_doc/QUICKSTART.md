# Quick Start Guide

Get started creating Instagram Reels in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.10+)
python3 --version

# Check FFmpeg installation
ffmpeg -version
```

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys
```

## Your First Reel

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run app.py
```

1. Enter your niche (e.g., "fitness", "cooking", "tech tips")
2. Optionally add keywords
3. Click "Generate Concepts"
4. Select one of the 3 concepts
5. Wait for video generation (2-5 minutes)
6. Download your Reel!

### Option 2: CLI

```bash
python cli.py
```

Follow the interactive prompts to create your Reel.

## Example Workflow

```
Input: "fitness" + "beginner-friendly, quick tips"
  ↓
Agent A generates 3 concepts:
  1. "5-Minute Morning Workout"
  2. "Kitchen Exercises for Busy People"
  3. "Desk Stretches for Office Workers"
  ↓
You select: Concept 1
  ↓
Agent B creates script + image prompts
  ↓
Agent C generates 5-8 images
  ↓
Agent D creates voiceover + assembles video
  ↓
Final 30-second Instagram Reel ready!
```

## Tips for Best Results

1. **Be Specific**: Instead of "cooking", try "quick healthy meals for students"
2. **Add Keywords**: Include style preferences like "trending", "educational", "entertaining"
3. **Review Concepts**: All 3 concepts are different - choose the one that resonates
4. **Be Patient**: Image and video generation takes time (2-5 minutes total)

## Troubleshooting

**"FFmpeg not found"**
- Install FFmpeg: `brew install ffmpeg` (macOS) or `sudo apt-get install ffmpeg` (Linux)

**"API key error"**
- Check your `.env` file exists and has correct keys
- Verify keys are valid and have credits

**"Rate limit exceeded"**
- Wait a few minutes and try again
- The system includes automatic rate limiting

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup instructions
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Explore the code to customize agents and workflows

Happy Reel creating! 🎬
