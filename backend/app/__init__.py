from flask import Flask
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints or routes
    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
