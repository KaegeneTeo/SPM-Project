from flask import Flask, jsonify, Blueprint, request, abort, current_app
from flask_supabase import Supabase
from datetime import datetime, timedelta

supabase_extension = Supabase()

mainapp = Blueprint("mainapp", __name__)

def calculate_recurring_dates(approved_dates):
    if not approved_dates:
        return []
    # Given a list of approved dates, calculate all recurring dates for the next year
    date_list = []
    earliest_date = min([datetime.strptime(date, '%Y-%m-%d') for date in approved_dates])
    print(earliest_date)
    end_date = earliest_date + timedelta(days=365)

    # Determine the days of the week for the approved dates
    approved_weekdays = [date.weekday() for date in [datetime.strptime(date, '%Y-%m-%d') for date in approved_dates]]

    current_date = earliest_date
    while current_date <= end_date:
        if current_date.weekday() in approved_weekdays:
            date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list

def create_schedule_entries(staff_id, dates, time_slot):
    # Create schedule entries for each date in the provided list

    for date in dates:
        response = supabase_extension.client.from_("schedule").insert({
            "staff_id": staff_id,
            "date": date,
            "time_slot": time_slot
        }).execute()

        if response == None:
            current_app.logger.error("Failed to create schedule entry for date %s: %s", date, response)

# Routes
@mainapp.route("/") 
def test():
    return "Hello world", 200

@mainapp.route("/employees", methods=['GET'])
def get_employees():
    response = supabase_extension.client.from_('Employee').select("*").execute()
    return response.data

@mainapp.route("/employees", methods=['PUT'])
def update_employee():
    form_data = request.form

@mainapp.route("/login", methods=['POST'])
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
    
@mainapp.route("/logout", methods=['POST'])
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
    

@mainapp.route("/check_auth", methods=['POST'])
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