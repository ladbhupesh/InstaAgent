# Azure OpenAI Setup Guide

This guide provides detailed instructions for setting up Azure OpenAI with the Instagram Reels AI Creator.

## Prerequisites

- Azure account with active subscription
- Access to Azure OpenAI service (may require approval)
- Python 3.10+ installed

## Step 1: Create Azure OpenAI Resource

1. **Navigate to Azure Portal:**
   - Go to [https://portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create New Resource:**
   - Click "Create a resource"
   - Search for "Azure OpenAI"
   - Click "Create"

3. **Configure Resource:**
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Select a region (e.g., East US, West Europe)
   - **Name**: Choose a unique name (e.g., `my-openai-resource`)
   - **Pricing Tier**: Select appropriate tier
   - Click "Review + create" then "Create"

4. **Wait for Deployment:**
   - Deployment takes 5-10 minutes
   - You'll receive a notification when complete

## Step 2: Get API Key and Endpoint

1. **Navigate to Your Resource:**
   - Go to "All resources" in Azure Portal
   - Find and click your Azure OpenAI resource

2. **Get Credentials:**
   - Click "Keys and Endpoint" in the left menu
   - Copy **KEY 1** (or KEY 2) - this is your `AZURE_OPENAI_API_KEY`
   - Copy the **Endpoint** URL - this is your `AZURE_OPENAI_ENDPOINT`
   - Note the format: `https://your-resource-name.openai.azure.com`

## Step 3: Deploy Models

You need to deploy two models:
1. **GPT-4** for text generation (concepts, scripts)
2. **DALL-E 3** for image generation

### Deploy GPT-4 Model

1. **Navigate to Model Deployments:**
   - In your Azure OpenAI resource, click "Model deployments"
   - Click "Create"

2. **Configure Deployment:**
   - **Model**: Select `gpt-4-turbo` or `gpt-4`
   - **Deployment name**: Choose a name (e.g., `gpt-4-turbo-deployment`)
   - **Model version**: Select latest (auto)
   - **Content filtering**: Enable if needed
   - Click "Create"

3. **Note the Deployment Name:**
   - This will be your `AZURE_OPENAI_DEPLOYMENT_NAME`
   - Example: `gpt-4-turbo-deployment`

### Deploy DALL-E 3 Model

1. **Create Another Deployment:**
   - Click "Create" again in Model deployments

2. **Configure Deployment:**
   - **Model**: Select `dall-e-3`
   - **Deployment name**: Choose a name (e.g., `dalle-3-deployment`)
   - **Model version**: Select latest (auto)
   - Click "Create"

3. **Note the Deployment Name:**
   - This will be your `AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME`
   - Example: `dalle-3-deployment`

## Step 4: Configure Environment Variables

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Azure OpenAI credentials:**
   ```env
   USE_AZURE_OPENAI=true
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo-deployment
   AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME=dalle-3-deployment
   ```

3. **Replace with your actual values:**
   - `your-api-key-here` → Your KEY 1 from Step 2
   - `your-resource-name` → Your resource name from Step 1
   - `gpt-4-turbo-deployment` → Your GPT-4 deployment name
   - `dalle-3-deployment` → Your DALL-E 3 deployment name

## Step 5: Verify Setup

Test your configuration:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('Azure OpenAI Config:')
print(f'  Use Azure: {os.getenv(\"USE_AZURE_OPENAI\")}')
print(f'  Endpoint: {os.getenv(\"AZURE_OPENAI_ENDPOINT\")}')
print(f'  Deployment: {os.getenv(\"AZURE_OPENAI_DEPLOYMENT_NAME\")}')
print(f'  Image Deployment: {os.getenv(\"AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME\")}')
"
```

## Troubleshooting

### Error: "AZURE_OPENAI_ENDPOINT not found"
- Check that `USE_AZURE_OPENAI=true` is set
- Verify endpoint URL is correct (no trailing slash)
- Ensure endpoint includes `https://`

### Error: "AZURE_OPENAI_DEPLOYMENT_NAME not found"
- Verify deployment names are correct
- Check that deployments are active in Azure Portal
- Ensure deployment names match exactly (case-sensitive)

### Error: "401 Unauthorized"
- Verify API key is correct
- Check that you copied the full key
- Ensure key hasn't been regenerated

### Error: "404 Not Found"
- Verify endpoint URL is correct
- Check that resource exists and is active
- Ensure deployment names match your Azure deployments

### Error: "Model not found"
- Verify model deployments are active
- Check deployment names match exactly
- Ensure models are available in your region

## API Version

The default API version is `2024-02-15-preview`. To use a different version:

1. Check available versions in Azure Portal
2. Update `AZURE_OPENAI_API_VERSION` in `.env`
3. Common versions:
   - `2024-02-15-preview` (recommended)
   - `2023-12-01-preview`
   - `2023-05-15`

## Cost Considerations

- **GPT-4 Turbo**: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- **DALL-E 3**: ~$0.04 per image (1024x1024), ~$0.08 per image (1024x1792)
- Monitor usage in Azure Portal → "Usage + estimated costs"

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use Azure Key Vault** for production deployments
3. **Rotate API keys** regularly
4. **Set up budget alerts** in Azure Portal
5. **Use separate deployments** for different environments

## Next Steps

Once Azure OpenAI is configured:
1. Complete ElevenLabs setup (see [SETUP.md](SETUP.md))
2. Test the system: `streamlit run app.py`
3. Create your first Reel!
