import requests
import google.generativeai as genai
import json
from bs4 import BeautifulSoup
from config import TARGET_URL, GEMINI_API_KEY, MODEL_NAME

# Configure the Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# Create the model
model = genai.GenerativeModel(MODEL_NAME)

def generate_tests():
    """Generates pytest tests from a target URL."""

    print(f"Fetching HTML from {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    html_content = str(soup.body)

    prompt = f"""
You are a test generator. Analyze the following HTML and propose up to 3 end-to-end user flows.

HTML:
```html
{html_content}
```

For each flow, provide a short title and a series of steps with CSS or text selectors.
Output a pure JSON array with the following structure:

[
    {{
        "id": "string",
        "title": "string",
        "steps": [
            {{ "action": "click"|"type", "selector": "string", "text": "string" (optional for type action) }}
        ]
    }}
]

Respond with only the JSON object.
"""

    print("Generating tests with Gemini...")
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        test_proposals = json.loads(json_text)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating or parsing tests: {e}")
        print(f"Raw response text: {response.text}")
        exit(1)

    generated_code = """
import pytest
from playwright.sync_api import Page, expect

"""

    for test in test_proposals:
        test_id = test['id']
        test_title = test['title']
        generated_code += f"""

def test_{test_id}(page: Page):
    """Generated test for: {test_title}"""
    print(f"\nRunning test: {test_title}")
    page.goto("{TARGET_URL}")

"""
        for step in test['steps']:
            action = step['action']
            selector = step['selector']
            text = step.get('text', '')

            if action == 'click':
                generated_code += f"    print('  - Clicking: {selector}')\n    page.locator(\"{selector}\").click()\n"
            elif action == 'type':
                generated_code += f"    print('  - Typing into: {selector}')\n    page.locator(\"{selector}\").type(\"{text}\")\n"
        
        generated_code += f"    print('Test completed successfully.')\n    # Add assertions here\n\n"

    output_path = "tests/generated/test_generated_flows.py"
    with open(output_path, "w") as f:
        f.write(generated_code)

    print(f"Successfully generated tests at {output_path}")

if __name__ == "__main__":
    generate_tests()
