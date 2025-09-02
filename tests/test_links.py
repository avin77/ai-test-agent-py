import pytest
import requests
from playwright.sync_api import Page
from config import TARGET_URL, BROWSERS
from urllib.parse import urljoin, urlparse

@pytest.mark.parametrize("browser_name", BROWSERS)
def test_link_audit(playwright, browser_name):
    """Audit all links on the target URL."""
    browser = getattr(playwright, browser_name).launch()
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    page.goto(TARGET_URL)

    links = page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")

    print(f"\nFound {len(links)} links on {TARGET_URL}")

    empty_hrefs = [link for link in links if not link]
    js_void_hrefs = [link for link in links if link == "javascript:void(0)"]
    hash_only_hrefs = [link for link in links if link == "#"]
    same_origin_broken_links = []

    target_domain = urlparse(TARGET_URL).netloc

    for link in links:
        if not link or link.startswith(("mailto:", "tel:")):
            continue

        link_domain = urlparse(link).netloc
        if link_domain == target_domain or not link_domain:
            absolute_link = urljoin(TARGET_URL, link)
            try:
                response = requests.get(absolute_link, timeout=5)
                if response.status_code >= 400:
                    same_origin_broken_links.append((absolute_link, response.status_code))
            except requests.RequestException as e:
                same_origin_broken_links.append((absolute_link, str(e)))

    print("\n--- Link Audit Report ---")
    if empty_hrefs:
        print(f"Found {len(empty_hrefs)} links with empty hrefs.")
    if js_void_hrefs:
        print(f"Found {len(js_void_hrefs)} javascript:void(0) links.")
    if hash_only_hrefs:
        print(f"Found {len(hash_only_hrefs)} hash-only links.")
    if same_origin_broken_links:
        print(f"Found {len(same_origin_broken_links)} broken same-origin links:")
        for link, status in same_origin_broken_links:
            print(f"  - {link} (Status: {status})")

    browser.close()

    assert not same_origin_broken_links, "Broken same-origin links found."
