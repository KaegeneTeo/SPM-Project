from flask import Flask
from flask_cors import CORS
from .routes import main

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
    "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin
    app.register_blueprint(main)
    return app