import json
import os
from scraper import fetch_page, parse_scholarships
from firebase import save_to_firestore, is_new_scholarship
from notifications import send_telegram_notification, send_webhooks_notifications

WEBHOOKS_JSON_PATH = os.path.join(os.path.dirname(__file__), "../configs/webhooks.json")


def validate_env_vars():
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")


def load_and_validate_webhooks():
    if not os.path.exists(WEBHOOKS_JSON_PATH):
        print(f"Webhooks JSON file not found. Defaulting to an empty array.")
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
        return webhooks
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {WEBHOOKS_JSON_PATH}: {e}")


def initialize_app():
    validate_env_vars()
    webhooks = load_and_validate_webhooks()
    return webhooks


def main(webhooks):
    html_content = fetch_page()
    if html_content:
        scholarships = parse_scholarships(html_content)
        new_scholarships = []
        for scholarship in scholarships:
            if is_new_scholarship(scholarship["url"]):
                new_scholarships.append(scholarship)
                send_telegram_notification(scholarship)
                send_webhooks_notifications(webhooks, scholarship)
        if new_scholarships:
            save_to_firestore(new_scholarships)


if __name__ == "__main__":
    try:
        webhooks = initialize_app()
        main(webhooks)
    except Exception as e:
        print(f"Error during initialization: {e}")
