import os
from dotenv import load_dotenv

load_dotenv()

# Get the base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-for-development'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'neuroapt.db')
    
    # Fix for psycopg3: Replace postgresql:// with postgresql+psycopg://
    if database_url and database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL_PRIMARY = "gpt-4o"  # For complex reasoning: final analysis, growth tracking
    OPENAI_MODEL_FAST = "gpt-4o-mini"  # For simple tasks: skill suggestions, micro tests
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    pass

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config
} 