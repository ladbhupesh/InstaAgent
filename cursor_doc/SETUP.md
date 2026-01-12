# Setup Guide

## Prerequisites

1. **Python 3.10+**: Ensure you have Python 3.10 or higher installed
2. **FFmpeg**: Required for video processing

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add to PATH

## Installation Steps

### 1. Clone and Navigate to Project
```bash
cd InstaAgent
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys. The system supports both Azure OpenAI and standard OpenAI.

**For Azure OpenAI (Recommended):**
```env
USE_AZURE_OPENAI=true
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-4-deployment-name
AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME=your-dalle-3-deployment-name
```

**For Standard OpenAI:**
```env
USE_AZURE_OPENAI=false
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Required for both:**
```env
ELEVENLABS_API_KEY=your-elevenlabs-key-here
```

**Optional:**
```env
REPLICATE_API_TOKEN=your-replicate-token-here
```

### 5. Get API Keys

#### Azure OpenAI (Recommended)

1. **Create Azure OpenAI Resource:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new "Azure OpenAI" resource
   - Note your endpoint URL (e.g., `https://your-resource-name.openai.azure.com`)

2. **Get API Key:**
   - In Azure Portal, go to your OpenAI resource
   - Navigate to "Keys and Endpoint"
   - Copy one of the API keys

3. **Create Deployments:**
   - Go to "Model deployments" in your Azure OpenAI resource
   - Deploy a GPT-4 model (e.g., `gpt-4-turbo`) - note the deployment name
   - Deploy DALL-E 3 model - note the deployment name
   - Use these deployment names in `.env`:
     - `AZURE_OPENAI_DEPLOYMENT_NAME` = GPT-4 deployment name
     - `AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME` = DALL-E 3 deployment name

4. **Set API Version:**
   - Use `2024-02-15-preview` or latest available version
   - Check Azure OpenAI documentation for current API versions

#### Standard OpenAI API Key (Alternative)
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy and paste into `.env`
5. Set `USE_AZURE_OPENAI=false`

#### ElevenLabs API Key
1. Go to [https://elevenlabs.io/](https://elevenlabs.io/)
2. Sign up or log in
3. Navigate to Profile → API Keys
4. Create a new API key
5. Copy and paste into `.env`

#### Replicate API Token (Optional)
1. Go to [https://replicate.com/](https://replicate.com/)
2. Sign up or log in
3. Navigate to Account → API Tokens
4. Create a new token
5. Copy and paste into `.env`

## Verification

Test your setup:

```bash
python -c "from utils.api_clients import OpenAIClient; print('OpenAI client initialized successfully')"
```

## Running the Application

### Streamlit UI (Recommended)
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### CLI Interface
```bash
python cli.py
```

## Troubleshooting

### FFmpeg Not Found
If you get an error about FFmpeg:
- Verify installation: `ffmpeg -version`
- Ensure FFmpeg is in your PATH
- Restart your terminal after installation

### API Key Errors
- Verify your `.env` file exists in the project root
- Check that API keys are correct (no extra spaces)
- Ensure you have credits/quota on your API accounts

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

### Rate Limiting
- The system includes automatic rate limiting
- If you hit limits, wait a few minutes and try again
- Consider upgrading your API plans for higher limits
