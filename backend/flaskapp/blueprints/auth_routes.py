# auth_controller.py
from flask import Blueprint, jsonify, request
from ..models.auth import AuthService
from ..extensions import supabase  # Assuming supabase is initialized here

# Initialize the Blueprint and the AuthService
auth_blueprint = Blueprint("auth", __name__)
auth_service = AuthService(supabase)

@auth_blueprint.route("/login", methods=['POST'])
def login():
    form_data = request.json
    # Delegate to the service
    json_response, status_code = auth_service.login(form_data['email'], form_data['password'])
    return jsonify(json_response), status_code

@auth_blueprint.route("/logout", methods=['POST'])
def logout():
    # Delegate to the service
    json_response, status_code = auth_service.logout()
    return jsonify(json_response), status_code

@auth_blueprint.route("/check_auth", methods=['POST'])
def check_auth():
    access_token = request.form.get('access_token')
    # Delegate to the service
    json_response, status_code = auth_service.check_auth(access_token)
    print(json_response, status_code)
    return jsonify(json_response), status_code
