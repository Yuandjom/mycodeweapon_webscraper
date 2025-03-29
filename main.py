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
        time.sleep(random.uniform(2, 4))  # Randomized sleep to mimic human loading time
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Simulate scrolling
        time.sleep(random.uniform(2, 4))  # Wait for elements to load

        html = driver.page_source  # Get full page HTML
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text(separator=" ")  # Extract all text with spaces
        
        # Extract structured information
        title = soup.find("div", class_="text-title-large").text.strip() if soup.find("div", class_="text-title-large") else "Title Not Found"
        # difficulty = soup.find("div", class_="text-difficulty").text.strip() if soup.find("div", class_="text-difficulty") else "Difficulty Not Found"
        # Extract difficulty from title text
        # Extract structured information from the raw text
        lines = text_content.split("\n")
        clean_lines = [line.strip() for line in lines if line.strip()]
        difficulty_lines = clean_lines[0]
        print(difficulty_lines)
        if "Easy" in difficulty_lines:
            difficulty = "Easy"
        elif "Medium" in difficulty_lines:
            difficulty = "Medium"
        elif "Hard" in difficulty_lines:
            difficulty = "Hard"
        else:
            difficulty = "Difficulty Not Found"        # Extract description

        description_element = soup.find("div", class_="elfjS")
        full_description = description_element.text.strip() if description_element else "Description Not Found"
        
        # Description block: stop at first keyword
        cutoff_keywords = ["Example", "Examples", "Constraints:", "Follow-up:"]
        cutoff_index = len(full_description)
        for keyword in cutoff_keywords:
            idx = full_description.find(keyword)
            if idx != -1:
                cutoff_index = min(cutoff_index, idx)
        description = full_description[:cutoff_index].strip()

        # Extract examples dynamically
        examples = []
        example_blocks = full_description.split("\nExample ")
        if len(example_blocks) > 1:
            for example in example_blocks[1:]:
                examples.append("Example " + example.strip().replace("\n", " "))

        # Extract constraints and follow-up
        constraints = []
        follow_up = "Follow-up Not Found"

        if "Constraints:" in full_description:
            constraints_section = full_description.split("Constraints:")[1]
            constraints_lines = constraints_section.split("\n")
            for line in constraints_lines:
                if line.strip() and "Follow-up:" not in line:
                    constraints.append(line.strip())

        if "Follow-up:" in full_description:
            follow_up_section = full_description.split("Follow-up:")[1]
            follow_up = follow_up_section.strip().split("\n")[0]  # Get only the first sentence
        # description = description.split("\nExample ")[0][0]
    finally:
        driver.quit()

    return {
        "title": title,
        "difficulty": difficulty,
        "description": description,
        "examples": examples,
        "constraints": constraints if constraints else ["Constraints Not Found"],
        "follow_up": follow_up,
        "testing": difficulty_lines,
        "full_description": full_description,

    }

@app.get("/leetcode/structured_text/{slug}")
def scrape_structured_text(slug: str):
    """
    API endpoint to return the structured text content of a LeetCode problem page.
    Example: GET /leetcode/structured_text/two-sum
    """
    return get_structured_text(slug)

@app.get("/")
def welcome():
    """
    Welcome endpoint to greet users and guide them on using the API.
    """
    return {
        "message": "👋 Welcome to the LeetCode Scraper API!",
        "usage": "To get structured data from a LeetCode problem, use the endpoint /leetcode/structured_text/{slug}.",
        "example": "/leetcode/structured_text/two-sum",
        "note": "Replace 'two-sum' with the slug of any LeetCode problem."
    }
