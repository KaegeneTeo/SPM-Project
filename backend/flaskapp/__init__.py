'''flaskapp'''

from flask import Flask, jsonify, request, abort, Blueprint
import os
from flask_supabase import Supabase
from flask_cors import CORS
from datetime import datetime, timedelta
from .schedules import schedule
from .main import mainapp

supabase_extension = Supabase()

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
        "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

    app.config['SUPABASE_URL'] = os.getenv("SUPABASE_URL")
    app.config['SUPABASE_KEY'] = os.getenv("SUPABASE_KEY")
    supabase_extension.init_app(app)

        # Methods

    app.register_blueprint(schedule)
    app.register_blueprint(mainapp)

    return app


