import os
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/notifications.log"), logging.StreamHandler()],
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_message(scholarship):
    message = (
        f"🎓 *Nueva Beca Disponible:*\n\n"
        f"🔹 {scholarship.get('title')}\n"
        f"🔗 {scholarship.get('url')}"
    )
    logging.debug(f"Generated message: {message}")
    return message


def send_telegram_notification(scholarship):
    try:
        message = get_message(scholarship)
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }
        logging.info(f"Sending Telegram notification to chat ID {TELEGRAM_CHAT_ID}.")
        response = requests.post(url, json=payload)
        if response.ok:
            logging.info(
                f"Telegram notification sent successfully: {response.status_code}"
            )
        else:
            logging.error(
                f"Failed to send Telegram notification. Status: {response.status_code}, Response: {response.text}"
            )
        return response.ok
    except requests.RequestException as e:
        logging.error(f"Error sending Telegram notification: {e}")
        return False


def send_webhooks_notifications(webhooks, scholarship):
    results = []
    for webhook in webhooks:
        headers = webhook.get("headers", {})
        body = webhook.get("additional_body", {}).copy()
        message_body_key = webhook.get("message_body_key")
        body[message_body_key] = get_message(scholarship)
        try:
            logging.info(f"Sending webhook notification to {webhook.get('url')}.")
            response = requests.request(
                method=webhook.get("method", "POST"),
                url=webhook.get("url"),
                headers=headers,
                json=body,
            )
            if response.ok:
                logging.info(
                    f"Webhook notification sent successfully to {webhook['url']}: {response.status_code}"
                )
            else:
                logging.error(
                    f"Webhook notification failed for {webhook['url']}. Status: {response.status_code}, Response: {response.text}"
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
            logging.error(
                f"Error sending webhook notification to {webhook['url']}: {e}"
            )
            results.append(
                {
                    "url": webhook["url"],
                    "success": False,
                    "error": str(e),
                }
            )
    return results
