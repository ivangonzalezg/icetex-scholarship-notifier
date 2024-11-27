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
    handlers=[logging.StreamHandler()],
)

parsed_url = urlparse(URL)

base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))


def fetch_page(url=URL):
    try:
        logging.info(f"Fetching page content from: {url}")
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            logging.info(f"Page fetched successfully. {url}")
            return response.content
        else:
            logging.warning(
                f"Failed to fetch page. Status code: {response.status_code}"
            )
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching page content: {e}")
        return None


def parse_scholarships(html_content) -> list[dict]:
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
        logging.info(f"Parsed {len(scholarships)} scholarships successfully.")
        return scholarships
    except Exception as e:
        logging.error(f"Error parsing scholarships: {e}")
        return []


def parse_scholarship(html_content) -> dict:
    logging.info("Parsing scholarship from HTML content.")
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        container = soup.select_one(".container .col-12.col-md-9")
        name = container.select_one("h1").get_text(strip=True)
        indicators = container.select(".indicadores_becas")
        indicators_data = {}
        for indicator in indicators:
            key, value = indicator.get_text(strip=True).split(":")
            indicators_data[key] = value
        openingdate = indicators_data.get("Apertura", "")
        deadlinedate = indicators_data.get("Cierre", "")
        resultsdate = indicators_data.get("Comisión nacional de becas", "")
        country = indicators_data.get("País", "")
        city = indicators_data.get("Ciudad", "")
        institution = indicators_data.get("Oferente", "")
        duration = indicators_data.get("Duración del programa", "")
        startdate = indicators_data.get("Fecha inicio", "")
        enddate = indicators_data.get("Fecha final", "")
        language = indicators_data.get("Idioma", "")
        mode = indicators_data.get("Tipo de curso", "")
        studyarea = indicators_data.get("Área de estudio", "")
        degree = indicators_data.get("Título a obtener", "")
        accordions = container.select(".container.acordeon-container .item_acord")
        funding = ""
        for accordion in accordions:
            section = accordion.select_one(".boton_acordeon").get_text(strip=True)
            if section == "Financiación":
                table = accordion.select_one(
                    ".zona-drop_acordeon .camp_html_acordeon table"
                )
                keys = []
                values = []
                extras = []
                rows = table.select("tr")
                for row in rows:
                    ths = row.select("th")
                    tds = row.select("td")
                    if len(ths) == 1:
                        for th in ths:
                            extras.append(th.get_text(strip=True))
                    if len(ths) > 1:
                        for th in ths:
                            keys.append(th.get_text(strip=True))
                    if len(tds) == 1:
                        for td in tds:
                            extras.append(td.get_text(strip=True))
                    if len(tds) > 1:
                        for td in tds:
                            values.append(td.get_text(strip=True))
                for index in range(len(keys)):
                    funding += f"*{keys[index]}:* {values[index]}\n"
                for extra in extras:
                    funding += f"{extra}\n"
        return {
            "name": name,
            "openingdate": openingdate,
            "deadlinedate": deadlinedate,
            "resultsdate": resultsdate,
            "country": country,
            "city": city,
            "institution": institution,
            "duration": duration,
            "startdate": startdate,
            "enddate": enddate,
            "language": language,
            "mode": mode,
            "studyarea": studyarea,
            "degree": degree,
            "funding": funding.strip(),
            "applicantprofile": "",
            "documents": "",
            "selectioncriteria": "",
        }
    except Exception as e:
        logging.error(f"Error parsing scholarship: {e}")
        return {}
