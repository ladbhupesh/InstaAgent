# Troubleshooting Guide

## ModuleNotFoundError: No module named 'moviepy.editor'

This error occurs when `moviepy` is not installed in the Python environment you're using.

### Solution 1: Install in the Correct Environment

**If using a virtual environment:**
```bash
# Activate your virtual environment first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Then install
pip install -r requirements.txt
```

**If using system Python:**
```bash
pip install moviepy
# or install all requirements
pip install -r requirements.txt
```

### Solution 2: Verify Python Environment

Check which Python you're using:
```bash
which python
python --version
python -c "import sys; print(sys.executable)"
```

If you're using Streamlit, check which Python Streamlit uses:
```bash
streamlit --version
```

### Solution 3: Reinstall moviepy

Sometimes a reinstall fixes the issue:
```bash
pip uninstall moviepy
pip install moviepy>=1.0.3
```

### Solution 4: Check IDE Python Interpreter

If using an IDE (VS Code, PyCharm, etc.):
1. Check which Python interpreter the IDE is using
2. Install packages in that specific interpreter
3. Or configure the IDE to use the correct Python environment

### Solution 5: Verify Installation

Test if moviepy can be imported:
```bash
python -c "from moviepy.editor import ImageClip; print('Success!')"
```

If this works but your app doesn't, you're likely using a different Python interpreter.

## Common Issues

### Issue: FFmpeg Not Found

**Error:** `RuntimeError: FFmpeg is not installed`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Issue: API Key Errors

**Error:** `ValueError: AZURE_OPENAI_API_KEY not found`

**Solution:**
1. Ensure `.env` file exists in project root
2. Check that environment variables are loaded:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
3. Verify variable names match exactly (case-sensitive)

### Issue: Import Errors in Streamlit

**Error:** Module not found when running `streamlit run app.py`

**Solution:**
1. Ensure Streamlit is using the correct Python:
   ```bash
   which streamlit
   ```
2. Install packages in the same environment:
   ```bash
   pip install -r requirements.txt
   ```
3. Restart Streamlit after installing packages

### Issue: Azure OpenAI Connection Errors

**Error:** `401 Unauthorized` or `404 Not Found`

**Solutions:**
- Verify API key is correct
- Check endpoint URL format: `https://your-resource.openai.azure.com`
- Ensure deployment names match exactly (case-sensitive)
- Verify API version is supported

### Issue: Rate Limiting

**Error:** Too many requests

**Solution:**
- The system includes automatic rate limiting
- Wait a few minutes and try again
- Check your API quotas in Azure Portal

## Getting Help

If issues persist:
1. Check the error message carefully
2. Verify all prerequisites are installed
3. Ensure you're using the correct Python environment
4. Review the setup documentation in `cursor_doc/SETUP.md`
