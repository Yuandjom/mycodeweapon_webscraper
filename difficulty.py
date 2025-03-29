from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
from bs4 import BeautifulSoup

app = FastAPI()

def get_structured_text(slug: str) -> dict:
    """Mimic human-like behavior to scrape and extract structured text from a LeetCode problem page."""
    url = f"https://leetcode.com/problems/{slug}/description/"

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Random User-Agent to mimic a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        time.sleep(random.uniform(3, 5))  # Randomized sleep to mimic human loading time
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Simulate scrolling
        time.sleep(random.uniform(2, 4))  # Wait for elements to load

        html = driver.page_source  # Get full page HTML
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text(separator=" ")  # Extract all text with spaces
        
        # Extract structured information from the raw text
        lines = text_content.split("\n")
        clean_lines = [line.strip() for line in lines if line.strip()]

        # Extract key components
        title = clean_lines[0] if clean_lines else "Title Not Found"
        difficulty = "Easy" if "Easy" in clean_lines else "Medium" if "Medium" in clean_lines else "Hard" if "Hard" in clean_lines else "Difficulty Not Found"

        # Find problem description
        description_index = clean_lines.index("Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.") if "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target." in clean_lines else -1
        description = " ".join(clean_lines[description_index:description_index+3]) if description_index != -1 else "Description Not Found"

        # Extract examples dynamically
        examples = []
        for i, line in enumerate(clean_lines):
            if line.startswith("Example"):
                example_text = []
                for j in range(i, len(clean_lines)):
                    if clean_lines[j].startswith("Constraints"):
                        break
                    example_text.append(clean_lines[j])
                examples.append("\n".join(example_text))

        # Extract constraints
        constraints_index = clean_lines.index("Constraints:") if "Constraints:" in clean_lines else -1
        constraints = clean_lines[constraints_index+1:constraints_index+5] if constraints_index != -1 else ["Constraints Not Found"]

        # Extract follow-up
        follow_up_index = clean_lines.index("Follow-up:") if "Follow-up:" in clean_lines else -1
        follow_up = clean_lines[follow_up_index+1] if follow_up_index != -1 else "Follow-up Not Found"

    finally:
        driver.quit()

    return {
        "title": title,
        "difficulty": difficulty,
        "description": description,
        "examples": examples,
        "constraints": constraints,
        "follow_up": follow_up
    }

@app.get("/leetcode/structured_text/{slug}")
def scrape_structured_text(slug: str):
    """
    API endpoint to return the structured text content of a LeetCode problem page.
    Example: GET /leetcode/structured_text/two-sum
    """
    return get_structured_text(slug)
