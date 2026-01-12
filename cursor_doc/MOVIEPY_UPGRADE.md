# MoviePy Version Upgrade Guide

## Current Status

The codebase supports both **MoviePy v1.x** and **v2.x** for maximum compatibility.

- **Installed version**: Check with `python -c "import moviepy; print(moviepy.__version__)"`
- **Latest version**: v2.2.1 (released May 21, 2025)
- **Your version**: v1.0.3 (if you haven't upgraded)

## MoviePy v2 Breaking Changes

According to the [official PyPI page](https://pypi.org/project/moviepy/), MoviePy v2.0 introduced major breaking changes:

### Import Changes

**v1.x (old):**
```python
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
```

**v2.x (new):**
```python
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
```

### Method Changes

**v1.x (old):**
```python
clip = ImageClip("image.png", duration=5)
clip = clip.resize((1920, 1080))
clip = clip.set_start(0)
clip = clip.set_audio(audio)
clip = clip.set_fps(30)
```

**v2.x (new):**
```python
clip = ImageClip("image.png").with_duration(5)
clip = clip.resized((1920, 1080))
clip = clip.with_start(0)
clip = clip.with_audio(audio)
clip = clip.with_fps(30)
```

## Upgrading to MoviePy v2

### Option 1: Upgrade to Latest (Recommended)

```bash
pip install --upgrade moviepy
```

This will install v2.2.1 (latest as of May 2025).

### Option 2: Stay on v1.x

If you prefer to stay on v1.x for compatibility:
```bash
pip install "moviepy>=1.0.3,<2.0.0"
```

## Code Compatibility

The codebase automatically detects which version you have installed and uses the appropriate API:

- **v1.x**: Uses `moviepy.editor` imports and `set_*` methods
- **v2.x**: Uses direct `moviepy` imports and `with_*` methods

You don't need to change any code - it works with both versions!

## Verify Your Installation

Check which version you have:

```bash
python -c "import moviepy; print(moviepy.__version__)"
```

Or run the environment check:

```bash
python check_environment.py
```

## Troubleshooting

### If you get import errors after upgrading:

1. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. **Reinstall MoviePy:**
   ```bash
   pip uninstall moviepy
   pip install moviepy
   ```

3. **Verify installation:**
   ```bash
   python -c "from moviepy import ImageClip; print('v2 works!')"
   # or
   python -c "from moviepy.editor import ImageClip; print('v1 works!')"
   ```

## Migration Resources

- [MoviePy v2 Documentation](https://zulko.github.io/moviepy/)
- [PyPI Package Page](https://pypi.org/project/moviepy/)
- [Migration Guide](https://zulko.github.io/moviepy/) (check the v1 to v2 migration section)

## Recommendation

**Upgrade to v2.2.1** for:
- Latest features and bug fixes
- Better performance
- Active maintenance
- Future-proofing

The codebase is already compatible with both versions, so upgrading is safe!
