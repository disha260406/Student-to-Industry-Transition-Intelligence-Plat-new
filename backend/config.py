import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'student_industry_db'
    
    # ML Model Configuration
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models')
    DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24

    # GitHub API Token (optional but recommended — raises rate limit from 60 to 5000/hr)
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or ''
