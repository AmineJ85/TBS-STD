import os

class Config:
    SECRET_KEY = 'YOUR_SECRET_KEY'
    API_TITLE = "TBS REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    
    # MySQL Config
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'YOUR_MYSQL_PASSWORD'
    MYSQL_DB = 'pfe'
    
    # Flask debug mode
    DEBUG = True  