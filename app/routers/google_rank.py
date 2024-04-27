from fastapi import FastAPI, APIRouter, HTTPException
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import logging

app = FastAPI()
router = APIRouter()

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.get("/google/get-rank")
async def get_rank(keyword: str, userdomain: str, pageCount: int):
    try:
        results = await scrape_google(keyword, userdomain, pageCount)
        return results
    except Exception as e:
        logger.exception("An unexpected error occurred while processing the request.")
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_google(keyword, userdomain, pageCount):
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

    try:
        results = []
        counter = 0
        for page in range(1, pageCount + 1):
            url = f"http://www.google.com/search?gl=uk&hl=en&q={keyword}&start={(page - 1) * 10}"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            search = soup.find_all("div", class_="yuRUbf")

            for h in search:
                if h.a and h.a.h3:
                    counter += 1
                    title = h.a.h3.text
                    link = h.a.get("href")
                    domain = urlparse(link).netloc
                    rank = counter
                    if domain == userdomain:
                        results.append({"title": title, "url": link, "domain": domain, "rank": rank})

    finally:
        driver.quit()

    return results

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
