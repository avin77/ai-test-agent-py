import pytest
from playwright.sync_api import Page, expect
from config import TARGET_URL, VIEWPORTS
from gemini_agent import check_ui_with_gemini

@pytest.mark.parametrize("width, height", VIEWPORTS)
def test_visual_inspection(page: Page, width, height, browser_name: str):
    """Perform a visual inspection of the target URL."""
    page.set_viewport_size({"width": width, "height": height})

    page.goto(TARGET_URL)
    page.wait_for_load_state("networkidle")

    screenshot = page.screenshot(full_page=True)

    report = check_ui_with_gemini(screenshot, TARGET_URL)

    if report:
        print(f"\nReport for {browser_name} at {width}x{height}:")
        print(f"  Verdict: {report.verdict}")
        print(f"  Summary: {report.summary}")
        for issue in report.issues:
            print(f"  - [{issue.severity.upper()}] {issue.area}: {issue.desc}")
        
        assert report.verdict == "pass", "Visual issues found"
    else:
        pytest.fail("Failed to get a valid report from Gemini.")
