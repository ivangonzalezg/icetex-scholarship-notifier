import firebase_admin
import os
import uuid
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

collection = "scholarships"

firebase_config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "configs/firebase.json"
)

firebase_admin.initialize_app(credentials.Certificate("./configs/firebase.json"))

db = firestore.client()


def is_new_scholarship(scholarship_url):
    existing = (
        db.collection(collection)
        .where(filter=FieldFilter("url", "==", scholarship_url))
        .limit(1)
        .get()
    )
    return not existing


def save_to_firestore(data):
    for item in data:
        item["timestamp"] = firestore.SERVER_TIMESTAMP
        db.collection(collection).add(document_data=item)
