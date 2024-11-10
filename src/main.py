from scraper import fetch_page, parse_scholarships
from firebase import save_to_firestore, is_new_scholarship
from notifications import send_telegram_notification, send_webhooks_notifications


def main():
    html_content = fetch_page()
    if html_content:
        scholarships = parse_scholarships(html_content)
        new_scholarships = []
        for scholarship in scholarships:
            if is_new_scholarship(scholarship["url"]):
                new_scholarships.append(scholarship)
                send_telegram_notification(scholarship)
                send_webhooks_notifications(scholarship)
        if new_scholarships:
            save_to_firestore(new_scholarships)


if __name__ == "__main__":
    main()
