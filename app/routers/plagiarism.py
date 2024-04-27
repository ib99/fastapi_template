from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse, quote_plus
import os
import logging

app = FastAPI()
router = APIRouter()

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options, executable_path="./chromedriver")
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

def search_google(text):
    driver = setup_driver()
    query = quote_plus(text)
    results = []
    try:
        for page in range(1, 3):
            url = f"http://www.google.com/search?q={query}&start={(page - 1) * 10}"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            search_results = soup.find_all("div", class_="yuRUbf")
            results.extend(h.a.get("href") for h in search_results if h.a)
    finally:
        driver.quit()
    return results

@router.get("/plagiarism/plagiarism-checker")
async def check_plagiarism(background_tasks: BackgroundTasks, text: str):
    background_tasks.add_task(check_plagiarism_task, text)
    return {"message": "Plagiarism check initiated"}

def check_plagiarism_task(text):
    results = search_google(text)
    if not results:
        logger.info("No results found for plagiarism check.")
        return
    for result in results:
        try:
            response = urllib.request.urlopen(result)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            plain_text = soup.get_text()
            if text in plain_text:
                logger.info(f"Plagiarism detected: {result}")
                return
        except Exception as e:
            logger.error(f"Error processing {result}: {e}")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
