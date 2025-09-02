ai-test-agent-py/
  GEMINI.md
  README.md
  requirements.txt
  config.py
  gemini_agent.py
  tests/
    test_visual.py
    test_links.py
    generated/          # auto created by generator
  generator/
    generate_tests_from_site.py


# Goal
Create and maintain a Python-only web UI testing project that:
- Uses Playwright for Python to open Chromium, Firefox, and WebKit
- Runs tests at multiple viewports
- Calls Gemini Vision to do visual checks on screenshots
- Prints clear results to console
- Includes a basic link audit test
- Includes a generator script that reads a target site and proposes new pytest cases
- Does not use environment variables. API key and target URL are stored in code in config.py.

# Constraints
- Python only. No Node scripts inside this repo.
- Put API key and target URL as string constants in config.py. Use placeholders that the user will replace.
- Keep prompts strict. Ask for JSON only and validate it.
- Be verbose in comments so any new reader understands the flow.

# Files to create or update

## requirements.txt
Create with these packages:
- playwright
- pytest
- google-generativeai
- pydantic
- requests
- beautifulsoup4

## README.md
Write a beginner friendly guide:
- What this repo does
- How to install
- How to set API key and target URL inside config.py
- How to run tests
- How to run the generator
- How to add a new test by hand

## config.py
Create constants:
- GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
- TARGET_URL = "https://playwright.dev"
- MODEL_NAME = "gemini-1.5-pro"
- VIEWPORTS = list of tuples for desktop, laptop, tablet, mobile
- BROWSERS = ["chromium", "firefox", "webkit"]

Explain in comments that users should replace the API key and TARGET_URL.

## gemini_agent.py
Create a helper that:
- Takes a PNG screenshot (bytes) and a URL string
- Calls Gemini Vision with a strict prompt
- Extracts the first JSON object from the response
- Validates it with pydantic against the OracleReport schema
- Returns a typed object

JSON contract for the report:
{
  "oracle": "visual",
  "verdict": "pass" or "fail",
  "severity": "none"|"low"|"medium"|"high",
  "issues": [
    { "id": "string", "area": "header|nav|main|footer|global", "desc": "string", "severity": "low|medium|high" }
  ],
  "summary": "string"
}

Print helpful errors if the model returns non JSON.

## tests/test_visual.py
Create a pytest that:
- Parametrizes across BROWSERS and VIEWPORTS from config
- Opens TARGET_URL
- Waits for network idle
- Takes a full page screenshot
- Calls gemini_agent.check_ui_with_gemini
- Prints a one line summary and each issue
- Asserts report.verdict == "pass"

## tests/test_links.py
Create a pytest that:
- Parametrizes across BROWSERS and one desktop viewport
- Gathers all <a href> elements
- Reports totals and common problems:
  - empty href
  - javascript:void(0)
  - hash-only anchors like "#"
- For same origin links only, do a simple HTTP GET with requests to check status < 400
- Print a short report and fail if there are broken same origin links

## generator/generate_tests_from_site.py
Create a small script that:
- Loads TARGET_URL HTML with requests
- Sends the HTML to Gemini with a prompt:
  - Find top 3 user flows visible from the homepage
  - Propose minimal end to end steps with CSS or text selectors
  - Output pure JSON array with tests: id, title, steps [{action, selector, text?}]
- Generate a pytest file at tests/generated/test_generated_flows.py that:
  - For each test proposal, creates a pytest test that runs on chromium at laptop viewport
  - Executes click and type actions
  - Prints each step as it runs
  - Does not assert anything yet except that the page did not crash
- If generation fails, print the model text to console and exit nonzero

# Shell actions to run after writing files
- Create a venv and install deps
- Install Playwright browsers
- Print a final checklist with next commands

Commands:
1) python -m venv .venv
2) source .venv/bin/activate  (Windows: .venv\\Scripts\\activate)
3) pip install -r requirements.txt
4) python -m playwright install
5) echo "Replace API key in config.py then run: pytest -q"
