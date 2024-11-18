import logging
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/firebase.log"), logging.StreamHandler()],
)

collection = "scholarships"

try:
    logging.info("Initializing Firebase Admin SDK.")
    firebase_admin.initialize_app(credentials.Certificate("./configs/firebase.json"))
    db = firestore.client()
    logging.info("Firebase initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing Firebase: {e}")
    raise


def is_new_scholarship(scholarship_url):
    try:
        logging.info(f"Checking if the scholarship already exists: {scholarship_url}")
        existing = (
            db.collection(collection)
            .where(filter=FieldFilter("url", "==", scholarship_url))
            .limit(1)
            .get()
        )
        if existing:
            logging.info("Scholarship already exists in the database.")
        else:
            logging.info("New scholarship detected.")
        return not existing
    except Exception as e:
        logging.error(f"Error checking scholarship in Firestore: {e}")
        raise


def save_to_firestore(data):
    try:
        logging.info(f"Saving {len(data)} scholarships to Firestore.")
        for item in data:
            item["timestamp"] = firestore.SERVER_TIMESTAMP
            db.collection(collection).add(document_data=item)
            logging.info(
                f"Scholarship saved successfully: {item.get('url', 'No URL provided')}"
            )
    except Exception as e:
        logging.error(f"Error saving scholarships to Firestore: {e}")
        raise
