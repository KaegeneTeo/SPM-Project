from flask import Flask, jsonify, Blueprint, request, abort, current_app
from flask_supabase import Supabase
from datetime import datetime, timedelta
import os
from flask_cors import CORS
from .blueprints.schedules_routes import schedules_blueprint
from .blueprints.employees_routes import employees_blueprint
from .blueprints.requests_routes import requests_blueprint
from .blueprints.teams_routes import teams_blueprint
from .blueprints.auth_routes import auth_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
        "origins": "*", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

    app.register_blueprint(schedules_blueprint)
    app.register_blueprint(employees_blueprint)
    app.register_blueprint(requests_blueprint)
    app.register_blueprint(teams_blueprint)
    app.register_blueprint(auth_blueprint)
    return app

app = create_app()

if __name__ == '__main__': 
    app.run(debug=True, host="0.0.0.0")
