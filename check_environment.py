#!/usr/bin/env python3
"""Script to check if all required packages are installed."""

import sys

def check_import(module_name, import_statement=None):
    """Check if a module can be imported."""
    if import_statement is None:
        import_statement = f"import {module_name}"
    
    try:
        exec(import_statement)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Environment Check for Instagram Reels AI Creator")
    print("=" * 60)
    print(f"\nPython Version: {sys.version}")
    print(f"Python Executable: {sys.executable}\n")
    
    print("Checking required packages:\n")
    
    # Check MoviePy - either v1 or v2 is fine
    moviepy_v1 = check_import("moviepy (v1)", "from moviepy.editor import ImageClip, AudioFileClip")
    moviepy_v2 = check_import("moviepy (v2)", "from moviepy import ImageClip, AudioFileClip")
    moviepy_ok = moviepy_v1 or moviepy_v2
    
    if moviepy_ok:
        if moviepy_v2:
            print("✅ moviepy (v2.x detected)")
        else:
            print("✅ moviepy (v1.x detected)")
    
    checks = [
        ("elevenlabs", "from elevenlabs.client import ElevenLabs"),
        ("langgraph", "from langgraph.graph import StateGraph"),
        ("streamlit", "import streamlit"),
        ("pydantic", "from pydantic import BaseModel"),
        ("dotenv", "from dotenv import load_dotenv"),
        ("aiohttp", "import aiohttp"),
        ("tenacity", "from tenacity import retry"),
    ]
    
    results = []
    for name, import_stmt in checks:
        results.append(check_import(name, import_stmt))
    
    print("\n" + "=" * 60)
    all_ok = moviepy_ok and all(results)
    if all_ok:
        print("✅ All packages are installed correctly!")
        print("\nYou can now run:")
        print("  streamlit run app.py")
        print("  python cli.py")
    else:
        print("❌ Some packages are missing!")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        if not moviepy_ok:
            print("\nNote: MoviePy v1.x is installed. Consider upgrading to v2.x:")
            print("  pip install --upgrade moviepy")
    print("=" * 60)

if __name__ == "__main__":
    main()
