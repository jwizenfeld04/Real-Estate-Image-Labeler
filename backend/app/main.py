from dotenv import load_dotenv
from pathlib import Path
import os
from . import create_app

# Explicitly load .env from the project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    # Run in debug mode only if the APP_ENV is set to 'local'
    debug_mode = os.getenv("APP_ENV") == "local"

    # Bind to 0.0.0.0 and port 8080 to work with Cloud Run
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
