import requests
import urllib3
from bs4 import BeautifulSoup
from config import URL
from urllib.parse import urlparse, urlunparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parsed_url = urlparse(URL)

base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))


def fetch_page():
    response = requests.get(URL, verify=False)
    return response.content if response.status_code == 200 else None


def parse_scholarships(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    scholarships = []
    for entry in soup.select(".portlet-body .media"):
        title = entry.find("a").get_text(strip=True) if entry.find("a") else None
        url = entry.find("a", href=True)["href"] if entry.find("a", href=True) else None
        if url and not url.startswith("http"):
            url = base_url + url
        image = (
            entry.find("img", src=True)["src"] if entry.find("img", src=True) else None
        )
        if image and not image.startswith("http"):
            image = base_url + image
        scholarships.append({"title": title, "url": url, "image": image})
    return scholarships
