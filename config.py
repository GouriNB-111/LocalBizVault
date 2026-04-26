import os

class Config:
    # Secret key — uses environment variable on cloud, fallback for local
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'

    # Database — auto switches between local SQLite and cloud PostgreSQL
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    
    # Render gives 'postgres://' but SQLAlchemy needs 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload