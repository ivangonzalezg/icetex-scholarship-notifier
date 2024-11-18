import requests
import urllib3
import logging
from bs4 import BeautifulSoup
from config import URL
from urllib.parse import urlparse, urlunparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()],
)

parsed_url = urlparse(URL)

base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))


def fetch_page():
    try:
        logging.info(f"Fetching page content from: {URL}")
        response = requests.get(URL, verify=False)
        if response.status_code == 200:
            logging.info("Page fetched successfully.")
            return response.content
        else:
            logging.warning(
                f"Failed to fetch page. Status code: {response.status_code}"
            )
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching page content: {e}")
        return None


def parse_scholarships(html_content):
    logging.info("Parsing scholarships from HTML content.")
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        scholarships = []
        entries = soup.select(".portlet-body .media")
        logging.info(f"Found {len(entries)} entries to process.")
        for entry in entries:
            title = entry.find("a").get_text(strip=True) if entry.find("a") else None
            url = (
                entry.find("a", href=True)["href"]
                if entry.find("a", href=True)
                else None
            )
            if url and not url.startswith("http"):
                url = base_url + url
            image = (
                entry.find("img", src=True)["src"]
                if entry.find("img", src=True)
                else None
            )
            if image and not image.startswith("http"):
                image = base_url + image
            scholarships.append({"title": title, "url": url, "image": image})
            logging.debug(
                f"Parsed scholarship: Title={title}, URL={url}, Image={image}"
            )
        logging.info(f"Parsed {len(scholarships)} scholarships successfully.")
        return scholarships
    except Exception as e:
        logging.error(f"Error parsing scholarships: {e}")
        return []
