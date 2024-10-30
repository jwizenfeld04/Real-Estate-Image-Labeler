import os
import csv
from datetime import datetime
from google.cloud import firestore, storage

# Initialize Firestore and Google Cloud Storage clients
db = firestore.Client()
bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
collection_name = os.getenv("FIRESTORE_COLLECTION_NAME")
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# CSV file details
csv_file_name = "uploaded-properties.csv"
csv_columns = [
    "id",
    "property_address",
    "property_id",
    "property_url",
    "upload_timestamp",
    "batch",
]


def upload_images_and_initialize_firestore(
    local_folder, remote_folder, collection_name
):
    # Get the parent folder name
    batch_name = os.path.basename(local_folder)

    # Create CSV file if it doesn't exist
    if not os.path.exists(csv_file_name):
        with open(csv_file_name, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

    # Read existing CSV data
    csv_data = []
    try:
        with open(csv_file_name, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            csv_data = list(reader)
    except FileNotFoundError:
        print(f"Error: {csv_file_name} not found.")

    # Track the ID for new entries in the CSV
    next_id = len(csv_data) + 1 if csv_data else 1

    # Walk through the local folder
    for root, _, files in os.walk(local_folder):
        for file_name in files:
            # Check if file is an image
            if not file_name.endswith((".jpg", ".jpeg", ".png")):
                print(f"Skipping {file_name}, not a supported image format")
                continue

            # Define paths for local and remote storage
            local_file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_file_path, local_folder)
            remote_file_path = os.path.join(remote_folder, relative_path).replace(
                "\\", "/"
            )

            # Check if the image is already in the CSV
            existing_entry = next(
                (
                    entry
                    for entry in csv_data
                    if entry["property_url"] == remote_file_path
                ),
                None,
            )
            if existing_entry:
                print(f"Skipping {remote_file_path}, already exists in the CSV.")
                continue

            # Upload image to Google Cloud Storage
            blob = bucket.blob(remote_file_path)
            if blob.exists():
                print(
                    f"Skipping {remote_file_path}, already exists in Google Cloud Storage."
                )
            else:
                try:
                    blob.upload_from_filename(local_file_path)
                    print(
                        f"Successfully uploaded {local_file_path} to {remote_file_path}"
                    )
                except Exception as e:
                    print(
                        f"Failed to upload {local_file_path} to {remote_file_path}: {e}"
                    )
                    continue

            # Create document ID by replacing '/' with '_' in relative_path
            image_doc_id = relative_path.replace("/", "_").rsplit(".", 1)[0] + ".jpg"

            # Access the "labels" collection and then the "columbus-sold" subcollection
            image_doc_ref = db.collection(collection_name).document(image_doc_id)

            # Check if the image document is already initialized in Firestore
            if (
                image_doc_ref.get().exists
                and "initialized" in image_doc_ref.get().to_dict()
            ):
                print(f"Skipping already initialized image {image_doc_id} in Firestore")
            else:
                # Set image document fields in Firestore
                image_doc_ref.set(
                    {
                        "average_score": None,
                        "image_path": remote_file_path,
                        "labeled": False,
                        "location": "columbus-sold",
                        "property_address": image_doc_id.split("_pic")[0],
                        "room_type": None,
                        "room_type_labeled": False,
                        "room_type_labeled_user_id": None,
                        "room_type_served": False,
                        "room_type_timestamp": None,
                        "score_labeled_user_ids": [],
                        "score_served_count": 0,
                        "scores": [],
                        "total_label_count": 0,
                        "initialized": True,
                    },
                    merge=True,
                )
                print(f"Initialized image {image_doc_id} in Firestore")

            # Add the new entry to the CSV
            csv_data.append(
                {
                    "id": next_id,
                    "property_address": image_doc_id.split("_pic")[0],
                    "property_id": image_doc_id,
                    "property_url": remote_file_path,
                    "upload_timestamp": datetime.now().isoformat(),
                    "batch": batch_name,
                }
            )
            next_id += 1

            # Write the updated CSV data
            try:
                with open(csv_file_name, "w", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    writer.writerows(csv_data)
            except Exception as e:
                print(f"Error writing to {csv_file_name}: {e}")


# Example usage
local_folder = "data/raw/sample_property1"
remote_folder = "images/columbus-sold"
upload_images_and_initialize_firestore(local_folder, remote_folder, collection_name)
