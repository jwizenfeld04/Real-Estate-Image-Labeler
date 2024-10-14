import os
import random
from typing import Optional, Dict, Any, List
from datetime import timedelta, datetime
from google.cloud import firestore, storage


class FirestoreUtils:
    def __init__(self):
        # Default Credentials look for 'GOOGLE_APPLICATION_CREDENTIALS' in environment variables
        self.db = firestore.Client()
        self.stg = storage.Client()
        self.bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")
        self.storage_prefix = "images/columbus-sold"

    def get_random_unlabeled_image(
        self, is_score: bool = False
    ) -> Optional[Dict[str, str]]:
        """Fetch a random unlabeled image from Firestore."""
        collection_ref = self.db.collection("labels")

        if is_score:
            query = collection_ref.where(
                filter=firestore.FieldFilter("total_label_count", "<", 10)
            )
        else:
            query = collection_ref.where(
                filter=firestore.FieldFilter("room_type_served", "==", False)
            )

        # Add ordering by __name__ to ensure consistency
        query = query.order_by("__name__")

        # Get a random starting point by generating a random letter
        random_char = chr(random.randint(65, 90))  # Random uppercase letter
        query = query.start_at({"__name__": random_char}).limit(1)

        docs = list(query.stream())

        if not docs:
            return None

        doc = docs[0]
        selected_image_id = doc.id

        bucket = self.stg.bucket(self.bucket_name)
        blob = bucket.blob(self.get_path_from_image_id(selected_image_id))
        url = blob.generate_signed_url(expiration=timedelta(hours=1))

        if not is_score:
            doc.reference.update({"room_type_served": True})

        return {"id": selected_image_id, "url": url}

    def label_room_type(self, image_path: str, room_type: str, user_id: str) -> str:
        """Label room type for a given image in Firestore."""
        doc_ref = self.db.collection("labels").document(image_path)

        try:
            doc = doc_ref.get()
            if not doc.exists():
                return "Image document not found."

            doc_data = doc.to_dict()
            if doc_data.get("room_type_labeled"):
                return "Room type has already been labeled."

            doc_ref.update(
                {
                    "room_type": room_type,
                    "room_type_labeled": True,
                    "room_type_timestamp": datetime.utcnow().isoformat(),
                    "room_type_labeled_user_id": user_id,
                }
            )
            return f"Room type '{room_type}' for image '{image_path}' updated successfully."
        except Exception as e:
            return f"Error updating room type: {str(e)}"

    def label_score(
        self, image_path: str, score: int, other_labels: Dict[str, Any], user_id: str
    ) -> str:
        """Update the score and other labels for a given image in Firestore."""
        doc_ref = self.db.collection("labels").document(image_path)

        try:
            doc = doc_ref.get()
            if not doc.exists():
                return "Image document not found."

            doc_data = doc.to_dict()
            if doc_data.get("total_label_count", 0) >= 10 or user_id in doc_data.get(
                "score_labeled_user_ids", []
            ):
                return "You have already labeled this image."

            scores = doc_data.get("scores", [])
            scores.append(score)
            average_score = sum(scores) / len(scores)

            doc_ref.update(
                {
                    "scores": scores,
                    "average_score": average_score,
                    "other_labels": firestore.ArrayUnion([other_labels]),
                    "total_label_count": firestore.Increment(1),
                    "score_labeled_user_ids": firestore.ArrayUnion([user_id]),
                    "score_served": firestore.Increment(1),
                }
            )
            return f"Score of {score} added for image '{image_path}' successfully."
        except Exception as e:
            return f"Error updating score: {str(e)}"

    def get_image_id_from_path(self, image_path: str) -> str:
        """Extract image ID from the image path."""
        image_id_parts = image_path.split("/")
        return f"{image_id_parts[2]}_{image_id_parts[3]}"

    def get_path_from_image_id(self, image_id: str) -> str:
        """Convert image ID back to the original path format."""
        # Find the index where "pic" starts
        pic_index = image_id.find("pic")

        if pic_index == -1:
            raise ValueError("Invalid image ID format: 'pic' not found in the image ID")

        # Split the image_id into address and filename
        address = image_id[:pic_index].rstrip(
            "_"
        )  # Remove trailing underscore if present
        filename = image_id[pic_index:]

        return f"{self.storage_prefix}/{address}/{filename}"


def main():
    """Main function to handle the resync of images."""
    firestore_utils = FirestoreUtils()
    print(firestore_utils.get_random_unlabeled_image(is_score=False))


if __name__ == "__main__":
    main()
