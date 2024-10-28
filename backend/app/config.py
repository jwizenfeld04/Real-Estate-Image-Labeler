import os
from dotenv import load_dotenv

# Load environment variables from the .env file at the project root
load_dotenv()


class Config:
    def __init__(self):
        # Determine environment (local or gcp)
        self.APP_ENV = os.environ.get("APP_ENV", "local")  # default to "local"

        # Read environment variables
        self.FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
        self.GOOGLE_APPLICATION_CREDENTIALS = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.GOOGLE_CLOUD_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
        self.FIRESTORE_COLLECTION_NAME = os.environ.get("FIRESTORE_COLLECTION_NAME")
        self.FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")

        self._validate()

    def _validate(self):
        """Validate that the necessary environment variables are set correctly."""
        if not self.FLASK_SECRET_KEY:
            raise ValueError("FLASK_SECRET_KEY is not set.")

        # Only validate GOOGLE_APPLICATION_CREDENTIALS in local mode
        if self.APP_ENV == "local":
            try:
                # Attempt to open the GOOGLE_APPLICATION_CREDENTIALS file
                with open(self.GOOGLE_APPLICATION_CREDENTIALS, "r") as f:
                    print("Successfully accessed GOOGLE_APPLICATION_CREDENTIALS file.")
            except FileNotFoundError:
                raise ValueError(
                    f"GOOGLE_APPLICATION_CREDENTIALS does not exist at the given path: {self.GOOGLE_APPLICATION_CREDENTIALS}"
                )
            except Exception as e:
                raise ValueError(
                    f"Could not access GOOGLE_APPLICATION_CREDENTIALS due to an error: {e}"
                )

        if not self.GOOGLE_CLOUD_PROJECT_ID:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID is not set.")
        if not self.FIRESTORE_COLLECTION_NAME:
            raise ValueError("FIRESTORE_COLLECTION_NAME is not set.")
        if not self.FIREBASE_STORAGE_BUCKET:
            raise ValueError("FIREBASE_STORAGE_BUCKET is not set.")
