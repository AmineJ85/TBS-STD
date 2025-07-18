import os
import sys
from flask import Flask, render_template, redirect, url_for, request
from flask_smorest import Api
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Set Flask environment variables for debug mode
os.environ['FLASK_DEBUG'] = '1'
os.environ['FLASK_ENV'] = 'development'

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules after loading environment variables
from email_service import init_mail
from Endpoints.register import register_bp
from Endpoints.login import login_bp  
from Endpoints.student import student_bp
from Endpoints.admin import admin_bp
from Endpoints.password_reset import password_reset_bp

app = Flask(
    __name__,
    template_folder='HTML',
    static_folder='static'
)

# Enable debug mode directly on the app
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'YOUR_SECRET_KEY')
app.config["API_TITLE"] = "TBS REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"

# Base URL for email confirmation links
app.config['BASE_URL'] = os.environ.get('BASE_URL', 'http://localhost:5000')

# MySQL Config
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'YOUR_MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'pfe')

# Initialize MySQL and Smorest API
mysql = MySQL(app)
app.mysql = mysql
api = Api(app)

# Initialize Mail
init_mail(app)

# Register Blueprints
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(password_reset_bp)

# Frontend Route
@app.route('/')
def home():
    # Get message from query parameter if exists
    message = request.args.get('message')
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
