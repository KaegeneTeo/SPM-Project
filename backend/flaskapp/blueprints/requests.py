from flask import Flask, jsonify, Blueprint, request, abort, current_app
from datetime import datetime, timedelta
from flask_supabase import Supabase
supabase_extension = Supabase()
request = Blueprint("request", __name__)


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

@request.route("/", methods=["GET"])
def test():
    return jsonify("Hello world")

@request.route("/request/<request_id>", methods=['GET'])
def get_selected_request(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(access_token)

    # Retrieve selected request by request_id
    request_response = supabase_extension.client.from_("request").select("*").eq("request_id", request_id).execute()
    selected_request = request_response.data[0]

    if not request_response.data:
        abort(404, description="Request not found.")
    
    # Create the response and add CORS headers manually
    response = jsonify(selected_request)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    return response

@request.route("/request/<request_id>/approve", methods=['PUT', 'POST'])
def request_approve(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]
    result_reason = request.json.get('result_reason')  # Get result_reason from request body
    approved_dates = request.json.get("approved_dates")  # Get approved dates from the request
    print(access_token, result_reason, approved_dates)

    # Retrieve the request to be approved
    request_response = supabase_extension.client.from_("request").select("*").eq("request_id", request_id).execute()
    print(request_response)

    if not request_response.data:
        abort(404, description="Request not found.")
    
    # Extract the necessary details
    request_data = request_response.data[0]
    print(request_data)
    staff_id = request_data['staff_id']
    request_type = request_data['request_type']
    time_slot = request_data['time_slot']

    # If Recurring
    if request_type == 2:
        recurring_dates = calculate_recurring_dates(approved_dates)
        print(recurring_dates)
        create_schedule_entries(staff_id, recurring_dates, time_slot)

    # If Ad-hoc
    elif request_type == 1:
        create_schedule_entries(staff_id, approved_dates, time_slot)

    response = supabase_extension.client.from_("request").update({
        "status": 1,  # Approved status
        "result_reason": result_reason  # Store the result_reason
    }).eq("request_id", request_id).execute()

    if not response.data:
        abort(404, description="Request not found.")

    response = jsonify({"message": "Request approved successfully"})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Add CORS header
    return response

@request.route("/request/<request_id>/reject", methods=['PUT'])
def request_reject(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]
    result_reason = request.json.get('result_reason')  # Get result_reason from request body
    print(access_token, result_reason)

    response = supabase_extension.client.from_("request").update({
        "status": -1,  # Rejected status
        "result_reason": result_reason  # Store the result_reason
    }).eq("request_id", request_id).execute()

    if not response.data:
        abort(404, description="Request not found.")

    return {"message": "Request rejected successfully"}

@request.route("/requests/", methods=['POST'])
def create_request():
    form_data = request.json
    print(form_data)
    # Validate input
    if not form_data:
        return jsonify({"error": "No request data provided"}), 400
    try:
        # Insert new request into the Supabase database
        response = supabase_extension.client.from_("request").insert({
            "staff_id": form_data.get('staffid'),
            "reason": form_data.get("reason"),
            "status": form_data.get("status"),
            "startdate": form_data.get("startdate"),
            "enddate": form_data.get("enddate"),
            "time_slot": form_data.get("time_slot"),
            "request_type": form_data.get("request_type"),
        }).execute()
        # Check for errors in the response

        if response == None:
            current_app.logger.error("Database insert error: %s", response.status_code)
            return jsonify({"error": "Failed to insert data into the database"}), 500

        # If everything is fine, return the inserted request with a 201 status
        return jsonify(response.data[0]), 201
    except Exception as e:
        current_app.logger.error("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500
    
@request.route("/requests/<int:staff_id>", methods=['GET'])
def get_requests_by_staff(staff_id: int):
    try:
        # Retrieve requests for the specified staff_id from the Supabase database
        response = supabase_extension.client.from_("request").select("*").eq("staff_id", staff_id).execute()
        print(response)
        # Check for errors in the response
        if response == None:
            current_app.logger.error("Database query error: %s", response["error"]["message"])
            return jsonify({"error": response["error"]["message"]}), 500
        
        # If no requests found, return a 404
        if response.data == []:
            return jsonify({"error": "No requests found for this staff ID"}), 404

        # Return the retrieved requests with a 200 status
        return jsonify(response.data), 200

    except Exception as e:
        current_app.logger.error("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500