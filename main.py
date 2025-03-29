from fastapi import FastAPI, HTTPException, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

app = FastAPI()

def extract_slug_from_url(leetcode_url: str) -> str:
    """Extract the slug from a valid LeetCode problem description URL."""
    parsed = urlparse(leetcode_url)
    if not parsed.netloc.endswith("leetcode.com"):
        raise ValueError("URL must be from leetcode.com")
    match = re.match(r"^/problems/([^/]+)/description/?$", parsed.path)
    if not match:
        raise ValueError("URL must be a valid LeetCode problem description link")
    return match.group(1)

def get_structured_text(slug: str) -> dict:
    url = f"https://leetcode.com/problems/{slug}/description/"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        time.sleep(random.uniform(2, 4))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        text_content = soup.get_text(separator=" ")

        title_element = soup.find("div", class_="text-title-large")
        title = title_element.text.strip() if title_element else "Title Not Found"

        difficulty_line = text_content.split("\n")[0]
        if "Easy" in difficulty_line:
            difficulty = "Easy"
        elif "Medium" in difficulty_line:
            difficulty = "Medium"
        elif "Hard" in difficulty_line:
            difficulty = "Hard"
        else:
            difficulty = "Difficulty Not Found"

        description_element = soup.find("div", class_="elfjS")
        full_description = description_element.text.strip() if description_element else "Description Not Found"

        cutoff_keywords = ["Example", "Examples", "Constraints:", "Follow-up:"]
        cutoff_index = len(full_description)
        for keyword in cutoff_keywords:
            idx = full_description.find(keyword)
            if idx != -1:
                cutoff_index = min(cutoff_index, idx)
        description = full_description[:cutoff_index].strip()

        examples = []
        example_blocks = full_description.split("\nExample ")
        if len(example_blocks) > 1:
            for example in example_blocks[1:]:
                examples.append("Example " + example.strip().replace("\n", " "))

        constraints = []
        if "Constraints:" in full_description:
            constraints_section = full_description.split("Constraints:")[1]
            constraints_lines = constraints_section.split("\n")
            for line in constraints_lines:
                if line.strip() and "Follow-up:" not in line:
                    constraints.append(line.strip())

        follow_up = "Follow-up Not Found"
        if "Follow-up:" in full_description:
            follow_up_section = full_description.split("Follow-up:")[1]
            follow_up = follow_up_section.strip().split("\n")[0]

        hints = []
        try:
            hint_divs = soup.select("div.text-body.text-sd-foreground.mt-2.pl-7.elfjS")
            for div in hint_divs:
                text = div.get_text(separator=" ").strip()
                if text:
                    hints.append(text)
            if not hints:
                hints = ["No visible hints found."]
        except Exception as e:
            hints = [f"Failed to extract hints: {str(e)}"]

    finally:
        driver.quit()

    return {
        "title": title,
        "difficulty": difficulty,
        "description": description,
        "examples": examples,
        "constraints": constraints if constraints else ["Constraints Not Found"],
        "follow_up": follow_up,
        "hints": hints,
        "testing": difficulty_line,
        "full_description": full_description,
    }

@app.get("/leetcode/scrape")
def scrape_structured_text(url: str = Query(..., description="Full LeetCode problem URL")):
    """
    Accepts a full LeetCode URL, validates it, and returns structured problem data.
    Example: GET /leetcode/scrape?url=https://leetcode.com/problems/two-sum/description/
    """
    try:
        slug = extract_slug_from_url(url)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    return get_structured_text(slug)

@app.get("/")
def welcome():
    return {
        "message": "👋 Welcome to the LeetCode Scraper API!",
        "usage": "Use the endpoint /leetcode/scrape?url=https://leetcode.com/problems/your-problem/description/",
        "note": "Make sure to paste a valid LeetCode problem URL that ends with /description/"
    }