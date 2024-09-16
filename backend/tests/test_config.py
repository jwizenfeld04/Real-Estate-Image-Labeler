import pytest
from app.config import Config


@pytest.fixture
def set_env_vars(monkeypatch, tmp_path):
    fake_service_account_file = tmp_path / "fake_service_account.json"
    fake_service_account_file.write_text("{}")

    monkeypatch.setenv("FLASK_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("FIRESTORE_SERVICE_ACCOUNT_FILE", str(fake_service_account_file))
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT_ID", "test-google-cloud-project-id")
    monkeypatch.setenv("FIRESTORE_COLLECTION_NAME", "test-collection-name")
    monkeypatch.setenv("FIREBASE_STORAGE_BUCKET", "test-storage-bucket")

    return fake_service_account_file


def test_config_loaded(set_env_vars):
    """Test if configuration variables are loaded correctly."""
    config = Config()

    assert config.FLASK_SECRET_KEY == "test_secret_key"
    assert config.FIRESTORE_SERVICE_ACCOUNT_FILE == str(set_env_vars)
    assert config.GOOGLE_CLOUD_PROJECT_ID == "test-google-cloud-project-id"
    assert config.FIRESTORE_COLLECTION_NAME == "test-collection-name"
    assert config.FIREBASE_STORAGE_BUCKET == "test-storage-bucket"


def test_invalid_service_account_path(monkeypatch):
    """Test if invalid service account path raises ValueError."""
    monkeypatch.setenv(
        "FIRESTORE_SERVICE_ACCOUNT_FILE", "/invalid/path/to/service_account.json"
    )

    with pytest.raises(
        ValueError, match="FIRESTORE_SERVICE_ACCOUNT_FILE does not exist"
    ):
        Config()


def test_missing_env_var(monkeypatch, tmp_path):
    """Test if missing environment variable raises ValueError."""
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)

    with pytest.raises(ValueError, match="FLASK_SECRET_KEY is not set"):
        Config()
