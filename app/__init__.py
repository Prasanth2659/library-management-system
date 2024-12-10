from flask import Flask
from flask_migrate import Migrate
from app.models import db, bcrypt

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
