from flask import Flask
from .config import Config


def create_app():
    app = Flask(__name__)

    # Create an instance of Config class
    config = Config()

    # Set config from object
    app.config.from_object(config)

    # Set secret key from config instance
    app.secret_key = config.FLASK_SECRET_KEY

    # Register Blueprints or routes
    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
