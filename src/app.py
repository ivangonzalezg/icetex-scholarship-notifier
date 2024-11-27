import json
import os
import logging
from scraper import fetch_page, parse_scholarships, parse_scholarship
from firebase import save_to_firestore, is_new_scholarship
from notifications import send_telegram_notification, send_webhooks_notifications
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

WEBHOOKS_JSON_PATH = os.path.join(os.path.dirname(__file__), "../configs/webhooks.json")


def validate_env_vars():
    logging.info("Validating environment variables.")
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
    logging.info("All required environment variables are set.")


def load_and_validate_webhooks():
    logging.info("Loading and validating webhooks configuration.")
    if not os.path.exists(WEBHOOKS_JSON_PATH):
        logging.warning(f"Webhooks JSON file not found. Defaulting to an empty array.")
        return []
    try:
        with open(WEBHOOKS_JSON_PATH, "r") as file:
            webhooks = json.load(file)
        if not isinstance(webhooks, list):
            raise ValueError("Webhooks JSON must be a list of webhook configurations.")
        for index, webhook in enumerate(webhooks):
            if not isinstance(webhook, dict):
                raise ValueError(f"Webhook at index {index} must be a dictionary.")
            if "url" not in webhook or not isinstance(webhook["url"], str):
                raise ValueError(f"Webhook at index {index} is missing a valid 'url'.")
            if "method" in webhook and webhook["method"] not in [
                "POST",
                "PUT",
                "PATCH",
            ]:
                raise ValueError(
                    f"Webhook at index {index} has an invalid 'method'. Allowed: POST, PUT, PATCH."
                )
            if "message_body_key" not in webhook or not isinstance(
                webhook["message_body_key"], str
            ):
                raise ValueError(
                    f"Webhook at index {index} is missing 'message_body_key' or it is not a string."
                )
            if "headers" in webhook and not isinstance(webhook["headers"], dict):
                raise ValueError(
                    f"Webhook headers at index {index} must be a dictionary."
                )
            if "additional_body" in webhook and not isinstance(
                webhook["additional_body"], dict
            ):
                raise ValueError(
                    f"Webhook additional_body at index {index} must be a dictionary."
                )
        logging.info("Webhooks configuration successfully loaded and validated.")
        return webhooks
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in {WEBHOOKS_JSON_PATH}: {e}")
        raise ValueError(f"Invalid JSON format in {WEBHOOKS_JSON_PATH}: {e}")


def initialize_app():
    logging.info("Initializing application.")
    validate_env_vars()
    webhooks = load_and_validate_webhooks()
    return webhooks


def app(webhooks):
    logging.info("Starting app execution.")
    html_content = fetch_page()
    if html_content:
        logging.info("Page content successfully fetched.")
        scholarships = parse_scholarships(html_content)
        logging.info(f"Parsed {len(scholarships)} scholarships.")
        new_scholarships = []
        for scholarship in scholarships:
            if is_new_scholarship(scholarship["url"]):
                logging.info(f"New scholarship detected: {scholarship['url']}")
                scholarship_html_content = fetch_page(scholarship["url"])
                parsed_scholarship = parse_scholarship(scholarship_html_content)
                scholarship.update(parsed_scholarship)
                new_scholarships.append(scholarship)
                send_telegram_notification(scholarship)
                send_webhooks_notifications(webhooks, scholarship)
        if new_scholarships:
            logging.info(
                f"Saving {len(new_scholarships)} new scholarships to Firestore."
            )
            save_to_firestore(new_scholarships)
        else:
            logging.info("No new scholarships to save.")
    else:
        logging.warning("No HTML content fetched. Skipping processing.")


if __name__ == "__main__":
    try:
        webhooks = initialize_app()
        app(webhooks)
    except Exception as e:
        logging.error(f"Error during execution: {e}")
