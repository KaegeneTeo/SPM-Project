from flask import Flask, jsonify, Blueprint, request, abort, current_app
from datetime import datetime, timedelta
from flask_supabase import Supabase
supabase_extension = Supabase()
employees = Blueprint("employees", __name__)


@employees.route("/employees", methods=['GET'])
def get_employees():
    response = supabase_extension.client.from_('Employee').select("*").execute()
    return response.data

@employees.route("/employees", methods=['PUT'])
def update_employee():
    form_data = request.form


@employees.route("/getstaffid", methods=['GET'])
def get_staff_id():
    staff_id = request.headers.get('X-Staff-ID')
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    return {"message": "CORS is working", "staff_id": staff_id, "access_token": access_token}
