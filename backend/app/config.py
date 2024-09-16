import os


class Config:
    def __init__(self):
        # Read environment variables when the Config class is instantiated
        self.FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
        self.FIRESTORE_SERVICE_ACCOUNT_FILE = os.environ.get(
            "FIRESTORE_SERVICE_ACCOUNT_FILE"
        )
        self.GOOGLE_CLOUD_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
        self.FIRESTORE_COLLECTION_NAME = os.environ.get("FIRESTORE_COLLECTION_NAME")
        self.FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")

        self._validate()

    def _validate(self):
        """Validate that the necessary environment variables are set correctly."""
        if not self.FLASK_SECRET_KEY:
            raise ValueError("FLASK_SECRET_KEY is not set.")
        if not self.FIRESTORE_SERVICE_ACCOUNT_FILE or not os.path.exists(
            self.FIRESTORE_SERVICE_ACCOUNT_FILE
        ):
            raise ValueError(
                f"FIRESTORE_SERVICE_ACCOUNT_FILE does not exist at the given path: {self.FIRESTORE_SERVICE_ACCOUNT_FILE}"
            )
        if not self.GOOGLE_CLOUD_PROJECT_ID:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID is not set.")
        if not self.FIRESTORE_COLLECTION_NAME:
            raise ValueError("FIRESTORE_COLLECTION_NAME is not set.")
        if not self.FIREBASE_STORAGE_BUCKET:
            raise ValueError("FIREBASE_STORAGE_BUCKET is not set.")
