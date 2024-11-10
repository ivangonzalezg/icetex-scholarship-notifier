import json
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

file_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "configs/webhooks.json"
)


def get_message(scholarship):
    message = (
        f"🎓 *Nueva Beca Disponible:*\n\n"
        f"🔹 {scholarship.get('title')}\n"
        f"🔗 {scholarship.get('url')}"
    )
    return message


def send_telegram_notification(scholarship):
    message = get_message(scholarship)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    return response.ok


def send_webhooks_notifications(scholarship):
    webhooks = []
    with open(file_path, "r") as file:
        webhooks = json.load(file)
    results = []
    for webhook in webhooks:
        headers = webhook.get("headers", {})
        body = webhook.get("additional_body", {}).copy()
        message_body_key = webhook.get("message_body_key")
        body[message_body_key] = get_message(scholarship)
        try:
            response = requests.request(
                method=webhook.get("method", "POST"),
                url=webhook.get("url"),
                headers=headers,
                json=body,
            )
            results.append(
                {
                    "url": webhook["url"],
                    "success": response.ok,
                    "status_code": response.status_code,
                    "response_body": response.json() if response.ok else response.text,
                }
            )
        except requests.RequestException as e:
            results.append(
                {
                    "url": webhook["url"],
                    "success": False,
                    "error": str(e),
                }
            )
    return results
