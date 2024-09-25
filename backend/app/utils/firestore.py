import os
import random
from typing import Optional, Dict, Any, List
from datetime import timedelta, datetime
from google.cloud import firestore, storage

# To run main go to the root directory and run python -m backend.app.utils.firestore


class FirestoreUtils:
    def __init__(self):
        # Default Credentials look for 'GOOGLE_APPLICATION_CREDENTIALS' in environment variables
        self.db = firestore.Client()
        self.stg = storage.Client()
        self.bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")
        self.storage_prefix = "images/columbus-sold/"
        self.unlabeled_room_type_cache: List[str] = []
        self.unlabeled_image_cache: List[str] = []

    def get_random_unlabeled_image(self) -> Optional[Dict[str, str]]:
        """Fetch a random unlabeled image from the cached IDs."""
        if not self.unlabeled_image_cache:
            self.__refresh_image_cache()

        if not self.unlabeled_image_cache:
            return None

        selected_image_id = random.choice(self.unlabeled_image_cache)
        bucket = self.stg.bucket(self.bucket_name)
        blob = bucket.blob(selected_image_id)
        url = blob.generate_signed_url(expiration=timedelta(hours=1))

        self.db.collection("labels").document(selected_image_id).update(
            {"room_type_served": True}
        )
        self.unlabeled_image_cache.remove(selected_image_id)

        return {"id": selected_image_id, "url": url}

    def label_room_type(self, image_path: str, room_type: str, user_id: str) -> str:
        """Label room type for a given image in Firestore."""
        doc_ref = self.db.collection("labels").document(
            self._get_image_id_from_path(image_path)
        )

        try:
            doc = doc_ref.get()
            if not doc.exists:
                return "Image document not found."

            doc_data = doc.to_dict()
            if doc_data.get("room_type_labeled"):
                return "Room type has already been labeled."

            doc_ref.update(
                {
                    "room_type": room_type,
                    "room_type_labeled": True,
                    "room_type_served": False,
                    "room_type_timestamp": datetime.utcnow().isoformat(),
                    "room_type_labeled_user_id": user_id,
                }
            )

            self.unlabeled_image_cache.remove(self.get_image_id_from_path(image_path))

            return f"Room type '{room_type}' for image '{image_path}' updated successfully."
        except Exception as e:
            return f"Error updating room type: {str(e)}"

    def label_score(
        self, image_path: str, score: int, other_labels: Dict[str, Any], user_id: str
    ) -> str:
        """Update the score and other labels for a given image in Firestore."""
        doc_ref = self.db.collection("labels").document(
            self._get_image_id_from_path(image_path)
        )

        try:
            doc = doc_ref.get()
            if not doc.exists:
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

    def __sync_images_from_bucket(self):
        """Sync new images from Google Cloud Storage to Firestore."""
        existing_image_ids = self.__get_existing_image_ids()
        blobs = self.__get_blobs_from_prefix()

        batch = self.db.batch()
        batch_size = 0
        max_batch_size = 500

        for blob in blobs:
            image_path = blob.name
            image_id = self.get_image_id_from_path(image_path)

            if image_id in existing_image_ids:
                continue

            doc_ref = self.db.collection("labels").document(image_id)
            doc_data = self.create_initial_doc_data(image_path)

            batch.set(doc_ref, doc_data)
            batch_size += 1

            if batch_size >= max_batch_size:
                batch.commit()
                batch = self.db.batch()
                batch_size = 0

        if batch_size > 0:
            batch.commit()

    def __refresh_image_cache(self):
        """Refresh the cache of unlabeled image IDs."""
        self.unlabeled_image_cache = [
            doc
            for doc in self.db.collection("labels")
            .where("room_type_labeled", "==", False)
            .stream()
        ]

    def __get_blobs_from_prefix(self):
        """Retrieve all blobs from a specific prefix in the storage bucket."""
        bucket = self.stg.bucket(self.bucket_name)
        return bucket.list_blobs(prefix=self.storage_prefix)

    def __get_existing_image_ids(self) -> set:
        """Fetch all existing image document IDs in Firestore."""
        return set(doc.id for doc in self.db.collection("labels").stream())

    def get_image_id_from_path(self, image_path: str) -> str:
        """Extract image ID from the image path."""
        image_id_parts = image_path.split("/")
        return f"{image_id_parts[2]}_{image_id_parts[3]}"

    def get_path_from_image_id(self, image_id: str) -> str:
        """Reconstruct image path from image ID"""
        path = self.storage_prefix
        parts = image_id.split("_")
        pic_index = next(
            (i for i, part in enumerate(parts) if part.startswith("pic")), None
        )

        if pic_index is None:
            raise ValueError("Invalid image_id format: 'pic' not found")

        property_address = "_".join(parts[:pic_index])
        image_number = parts[pic_index].replace("pic", "")
        return path + property_address + "/" + image_number

    @staticmethod
    def create_initial_doc_data(image_path: str) -> Dict[str, Any]:
        """Create initial document data for a new image."""
        image_id_parts = image_path.split("/")
        return {
            # General ifno
            "property_address": image_id_parts[2],
            "image_path": image_path,
            "location": image_id_parts[1],
            "labeled": False,
            # Label 1: Room Type
            "room_type": None,
            "room_type_served": False,
            "room_type_labeled": False,
            "room_type_timestamp": None,
            "room_type_labeled_user_id": None,
            # Label 2: Scores
            "scores": [],
            "average_score": None,
            "other_labels": [],
            "score_served": 0,
            "total_label_count": 0,
            "score_labeled_user_ids": [],
        }


def main():
    """Main function to handle the resync of images."""
    firestore_utils = FirestoreUtils()
    firestore_utils.__refresh_image_cache()
    firestore_utils.__sync_images_from_bucket()


if __name__ == "__main__":
    main()
