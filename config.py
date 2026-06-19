import os
from dotenv import load_dotenv

load_dotenv()

# Get the base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-for-development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'neuroapt.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL_PRIMARY = "gpt-4o"  # For complex reasoning: final analysis, growth tracking
    OPENAI_MODEL_FAST = "gpt-4o-mini"  # For simple tasks: skill suggestions, micro tests 