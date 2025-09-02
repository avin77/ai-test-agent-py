import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
import json
from config import GEMINI_API_KEY, MODEL_NAME

# Pydantic models for validation
class Issue(BaseModel):
    id: str
    area: str
    desc: str
    severity: str

class OracleReport(BaseModel):
    oracle: str
    verdict: str
    severity: str
    issues: list[Issue]
    summary: str

def check_ui_with_gemini(screenshot_png: bytes, url: str) -> OracleReport | None:
    """Calls Gemini Vision to check for UI issues on a screenshot."""

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return None

    # Configure the Gemini API key
    genai.configure(api_key=GEMINI_API_KEY)

    # Create the model
    model = genai.GenerativeModel(MODEL_NAME)
    """Calls Gemini Vision to check for UI issues on a screenshot."""

    prompt = f"""
    You are a visual QA agent. Your task is to analyze a screenshot of a web page and identify any visual bugs or usability issues.

    The URL of the page is: {url}

    Analyze the screenshot and provide a report in JSON format. The JSON should follow this schema:

    {{
      "oracle": "visual",
      "verdict": "pass" or "fail",
      "severity": "none"|"low"|"medium"|"high",
      "issues": [
        {{ "id": "string", "area": "header|nav|main|footer|global", "desc": "string", "severity": "low|medium|high" }}
      ],
      "summary": "string"
    }}

    - `verdict`: "pass" if there are no issues, "fail" otherwise.
    - `severity`: The highest severity of all issues, or "none" if there are no issues.
    - `issues`: A list of all issues found.
    - `summary`: A brief summary of the findings.

    Respond with only the JSON object.
    """

    try:
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": screenshot_png}])
        
        # Extract the JSON from the response
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        report_data = json.loads(json_text)
        
        # Validate with pydantic
        report = OracleReport(**report_data)
        return report

    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Error parsing or validating Gemini response: {e}")
        print(f"Raw response text: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
