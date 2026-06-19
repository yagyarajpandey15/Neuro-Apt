from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()

# Custom JSON encoder for SQLAlchemy models
class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Use custom JSON encoder
    app.json_encoder = ModelEncoder
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize OpenAI client within app context
    with app.app_context():
        from neuroapt.app.utils.openai_api import init_openai_client
        init_openai_client()
    
    from neuroapt.app.routes.auth import auth_bp
    from neuroapt.app.routes.test import test_bp
    from neuroapt.app.routes.result import result_bp
    from neuroapt.app.routes.admin import admin_bp
    from neuroapt.app.routes.dashboard import dashboard_bp
    from neuroapt.app.routes.careers import careers as careers_bp
    from neuroapt.app.routes.main import main as main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(careers_bp)
    app.register_blueprint(main_bp)
    
    return app 