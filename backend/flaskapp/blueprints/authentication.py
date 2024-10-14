from flask import Flask, jsonify, Blueprint, request, abort, current_app
from datetime import datetime, timedelta
from flask_supabase import Supabase
supabase_extension = Supabase()

authentication = Blueprint("authentication", __name__)


@authentication.route("/auth", methods=['GET'])
def check_online():
    return "Hello authentication", 200

@authentication.route("/login", methods=['POST'])
def login():
    form_data = request.json
    try: 
        response = supabase_extension.client.auth.sign_in_with_password({
            "email": form_data['email'],
            "password": form_data['password']
        })

        json_response = {
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }   

        # Fetch staff_id from the Employee table
        staff_response = supabase_extension.client.from_("Employee").select("Staff_ID, Role, Dept, Reporting_Manager").ilike("Email", json_response["email"]).execute()
        
        if staff_response.data:
            # Fetch all team IDs associated with this staff ID
            
            json_response["staff_id"] = staff_response.data[0]["Staff_ID"]
            json_response["role"] = staff_response.data[0]["Role"]
            json_response["dept"] = staff_response.data[0]["Dept"]
            json_response["reporting_manager"] = staff_response.data[0]["Reporting_Manager"]
            # print(reporting_manager_id)
            
        else:
            json_response["staff_id"] = None  # Handle case if no staff data is found
            json_response["role"] = None
            json_response["dept"] = None
            json_response["reporting_manager"] = None
        return jsonify(json_response), 200

    except Exception as e:
        json_response = {
            "message": str(e),  # Use str(e) to get the error message
        }
        return jsonify(json_response), 400  # Use 400 for bad requests
    
@authentication.route("/logout", methods=['POST'])
def logout():
    try:
        # Call Supabase to sign the user out
        supabase_extension.client.auth.sign_out()
        return jsonify({"message": "User signed out successfully."}), 200
    except Exception as e:
        json = {
            "message": str(e),
        }
        return jsonify(json), 400
    

@authentication.route("/check_auth", methods=['POST'])
def check_auth():
    response = supabase_extension.client.auth.get_user(request.form['access_token'])
    status_code = None
    if response != None:
        json = {
            "email": response.user.email,
            "role": response.user.role,
            "access_token": request.form['access_token'],
            "refresh_token": request.form['refresh_token'],
        }
        status_code = 200
    else:
        json = {}
        status_code = 404
    return json, status_code

