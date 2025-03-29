# mycodeweapon_webscraper

A FastAPI-powered web scraper that collects and serves coding question data from websites like LeetCode and others. Designed to be lightweight, extensible, and easy to deploy.

## 🚀 Features

- Scrapes coding questions and metadata from target platforms
- REST API endpoints powered by FastAPI
- Easily extensible for new scraping targets
- Lightweight and modular project structure

## 📦 Tech Stack

- **Python 3.10+**
- **FastAPI** for API routing
- **Uvicorn** as ASGI server
- **BeautifulSoup / Requests** for scraping (or your preferred scraping tools)
- **Pydantic** for data models
- **dotenv** for environment variable management

---

## 🛠️ Setup & Installation
Clone the repository

```bash
git clone https://github.com/Yuandjom/mycodeweapon_webscraper.git
cd mycodeweapon_webscraper
```
## Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # On macOS/Linux
.\venv\Scripts\activate        # On Windows
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the app

```bash
uvicorn leetcode_scraper.main:app --reload
```

The FastAPI server will be available at:
👉 http://127.0.0.1:8000
👉 Swagger UI: http://127.0.0.1:8000/docs

