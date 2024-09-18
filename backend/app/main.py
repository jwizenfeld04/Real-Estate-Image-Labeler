from dotenv import load_dotenv
from . import create_app

# Load environment variables from the .env file at the project root
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
