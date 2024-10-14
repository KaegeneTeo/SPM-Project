from flask import Flask, jsonify, Blueprint, request, abort, current_app
from flask_supabase import Supabase
from datetime import datetime, timedelta
import os
from flask_cors import CORS
from blueprints.schedules import schedules
from blueprints.employees import employees
from blueprints.requests import requests
from blueprints.teams import teams
from blueprints.authentication import authentication

supabase_extension = Supabase()

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
        "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

    app.config['SUPABASE_URL'] = os.getenv("SUPABASE_URL")
    app.config['SUPABASE_KEY'] = os.getenv("SUPABASE_KEY")
    supabase_extension.init_app(app)

        # Methods

    app.register_blueprint(schedules)
    app.register_blueprint(employees)
    app.register_blueprint(requests)
    app.register_blueprint(teams)
    app.register_blueprint(authentication)
    return app

app = create_app()
if __name__ == '__main__': 
    app.run(debug=True, host="0.0.0.0")
