import os
import csv
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()
collection_name = os.getenv("FIRESTORE_COLLECTION_NAME")


def export_room_labeled_properties_to_csv():
    # Define the CSV file name and columns
    csv_file_name = "room_labeled_properties.csv"
    csv_columns = [
        "id",
        "property_id",
        "property_address",
        "room_type",
        "room_type_labeled",
        "room_type_labeled_user_id",
        "room_type_served",
        "room_type_timestamp",
        "score_labeled",
        "score_labeled_user_ids",
        "score_served_count",
        "scores",
        "total_label_count",
    ]

    # Query the collection and filter by room_type_labeled == True
    query = db.collection(collection_name).where(
        filter=firestore.FieldFilter("room_type_labeled", "==", True)
    )
    docs = query.stream()

    # Write the data to the CSV file
    try:
        with open(csv_file_name, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            row_id = 1
            for doc in docs:
                data = doc.to_dict()
                writer.writerow(
                    {
                        "id": row_id,
                        "property_id": doc.id,
                        "property_address": data["property_address"],
                        "room_type": data["room_type"],
                        "room_type_labeled": data["room_type_labeled"],
                        "room_type_labeled_user_id": data["room_type_labeled_user_id"],
                        "room_type_served": data["room_type_served"],
                        "room_type_timestamp": data["room_type_timestamp"],
                        "score_labeled": data["labeled"],
                        "score_labeled_user_ids": data["score_labeled_user_ids"],
                        "score_served_count": data["score_served_count"],
                        "scores": data["scores"],
                        "total_label_count": data["total_label_count"],
                    }
                )
                row_id += 1

        print(f"CSV file '{csv_file_name}' created successfully.")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")


# Example usage
export_room_labeled_properties_to_csv()
