import os

# ---
# CONFIG
# ---

# Get the Gemini API key from the environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# The target URL to test
TARGET_URL = "https://play.ezygamers.com"

# The model to use for visual checks
MODEL_NAME = "gemini-2.0-flash"

# Viewports to test
VIEWPORTS = [
    (1920, 1080),  # Desktop
    (1366, 768),   # Laptop
    (768, 1024),    # Tablet
    (390, 844),     # Mobile
]

# Browsers to test
BROWSERS = ["chromium"]