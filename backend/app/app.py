from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request, abort
from flask_cors import CORS
from datetime import datetime, timedelta
app = Flask(__name__)
CORS(app, credentials=True ,resources={r"/*": {
    "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Methods
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
    # Placeholder value to test, need set auto increment in our db
    schedule_id = 6

    for date in dates:
        response = supabase.table("schedule").insert({
            "schedule_id": schedule_id,
            "staff_id": staff_id,
            "date": date,
            "time_slot": time_slot
        }).execute()

        if response == None:
            app.logger.error("Failed to create schedule entry for date %s: %s", date, response)

        schedule_id += 1

# Routes
@app.route("/")
def test():
    return "Hello world", 200

@app.route("/teams_by_dept", methods=['GET'])
def get_teams():
    department = request.args.get('department')
    
    staff_list = []
    team_list = []
    # Query the database
    response = supabase.from_('Employee').select('Staff_ID').eq("Dept", department).execute()
    for item in response.data:
        staff_list.append(item['Staff_ID'])

    for id in staff_list:
        response = supabase.from_('team').select('team_id').eq('staff_id', id).execute()
        for i in response.data:
            if i['team_id'] not in team_list:
                team_list.append(i['team_id'])
    # Check if the query was successful and return the data
    if team_list!=[]:
        print(team_list)
        return team_list  # Return the retrieved teams as JSON
    else:    
        return jsonify({"error: No teams found"}), 400  # Return error if query fails

   

@app.route("/schedules", methods=['GET'])
def get_schedules():
    return jsonify("hello")
    data = request.json
    
    print(data)
    keys = list(data.keys())
    dict1 = {}
    if "staff_id" in keys:
        allnames = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Staff_ID", data["staff_id"]).execute()
        response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule(Schedule_ID, Staff_ID, Date, Time_Slot)').eq("Staff_ID", data["staff_id"]).execute()
    elif "dept" in keys:
        if "team" in keys:
            allnames = supabase.from_('Employee').select('Staff, Staff_FName, Staff_LName, team(staff_id, team_id)').eq("team_id", data["team"]).eq("Dept", data["dept"]).execute()
            response = supabase.from_('Employee').select('Staff, Staff_FName, Staff_LName, Dept, schedule(Schedule, Staff, Date, Time_Slot), team(staff_id, team_id)').eq("team_id", data["Team"]).eq("Dept", data["dept"]).execute()  
        else:
            allnames = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).execute()
            response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule(Schedule_ID, Staff_ID, Date, Time_Slot)').eq("Dept", data["dept"]).execute()  
    responselist = list(response.data)
    
    for i in range(0, len(responselist)):
        dict1 = dict1.get((responselist[i]["Date"], responselist[i]["Time_Slot"]), {
            "Date": responselist[i]["Date"],
            "Time_Slot": responselist[i]["Time_Slot"],
            "Name_List": list(responselist[i]["Staff_ID"] + " - " + responselist[i]["Staff_FName"] + " " + responselist[i]["Staff_LName"])
            })["Name_List"].append(responselist[i]["Staff_ID"] + " - " + responselist[i]["Staff_FName"] + " " + responselist[i]["Staff_LName"])
    dict2 = {}
    for key in list(dict1.keys()):
        if dict1[key]["Time_Slot"] == "AM":
            dict2[key] = {
            "start": str(dict1[key]["Date"]) + " 09:00",
            "end": str(dict1[key]["Date"]) + " 13:00",
            "class": "AM",
            "Name_List": dict1[key]["Name_List"]
            }
        if dict1[key]["Time_Slot"] == "PM":
            dict2[key] = {
            "start": str(dict1[key]["Date"]) + " 14:00",
            "end": str(dict1[key]["Date"]) + " 18:00",
            "class": "PM",
            "Name_List": dict1[key]["Name_List"]
            }
            
        return jsonify({"schedules": dict2, "allnames": allnames})

@app.route("/employees", methods=['GET'])
def get_employees():
    response = supabase.table('Employee').select("*").execute()
    return response.data

@app.route("/employees", methods=['PUT'])
def update_employee():
    form_data = request.form

@app.route("/login", methods=['POST'])
def login():
    form_data = request.json
    try: 
        response = supabase.auth.sign_in_with_password({
            "email": form_data['email'],
            "password": form_data['password']
        })

        json_response = {
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }   

        # Fetch staff_id from the Employee table
        staff_response = supabase.table("Employee").select("Staff_ID, Role, Dept").ilike("Email", json_response["email"]).execute()
        
        if staff_response.data:
            # Fetch all team IDs associated with this staff ID
            team_response = supabase.table("team").select("team_id").eq("staff_id", staff_response.data[0]["Staff_ID"]).execute()
            
            json_response["staff_id"] = staff_response.data[0]["Staff_ID"]
            json_response["role"] = staff_response.data[0]["Role"]
            json_response["dept"] = staff_response.data[0]["Dept"]

            # Check if multiple teams are found
            if team_response.data:
                team_ids = [team["team_id"] for team in team_response.data] 
                if team_ids:
                    json_response["team"] = team_ids 
                else:
                    json_response["team"] = [None]   # Return empty list or None as needed
        else:
            json_response["staff_id"] = None  # Handle case if no staff data is found
            json_response["role"] = None

        print(json_response)
        return jsonify(json_response), 200

    except Exception as e:
        json_response = {
            "message": str(e),  # Use str(e) to get the error message
        }
        return jsonify(json_response), 400  # Use 400 for bad requests
    
@app.route("/logout", methods=['POST'])
def logout():
    try:
        # Call Supabase to sign the user out
        supabase.auth.sign_out()
        return jsonify({"message": "User signed out successfully."}), 200
    except Exception as e:
        json = {
            "message": str(e),
        }
        return jsonify(json), 400
    

@app.route("/check_auth", methods=['POST'])
def check_auth():
    response = supabase.auth.get_user(request.form['access_token'])
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


@app.route('/team/requests', methods=['GET'])
def get_team_requests():
    staff_id = request.headers.get('X-Staff-ID')
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(staff_id, access_token)
    
    # Retrieve Team_ID(s) of current logged in user and store in list
    team_ids_response = supabase.table("team").select("team_id").eq("staff_id", staff_id).execute()
    team_ids = [team['team_id'] for team in team_ids_response.data]
    print("Retrieved team_ids:", team_ids)

    # Throw error if no team_ids
    if not team_ids:
        abort(404, description="No team found for the logged-in user.")

    # Retrieve Staff_ID(s) of staff belonging to the team(s) of the current logged-in user
    staff_ids_response = supabase.table("team").select("staff_id").in_("team_id", team_ids).neq("staff_id", staff_id).execute()
    
    staff_ids = [staff['staff_id'] for staff in staff_ids_response.data]
    print("Retrieved staff_ids:", staff_ids)
    
    # Throw error if no staff members are found
    if not staff_ids:
        abort(404, description="No staff found for the provided team IDs.")
    
    # Retrieve all requests of staff belonging to team(s) of logged in user
    requests_response = supabase.table("request").select("*").in_("staff_id", staff_ids).execute()
    
    requests = requests_response.data
    print("Retrieved requests:", requests)
    
    # Check if requests are found, else throw an error message
    if not requests:
        abort(404, description="No requests found for staff members in these teams.")
    
    # Create the response and add CORS headers manually
    response = jsonify(requests)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    return response
   
@app.route("/request/<request_id>", methods=['GET'])
def get_selected_request(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(access_token)

    # Retrieve selected request by request_id
    request_response = supabase.table("request").select("*").eq("request_id", request_id).execute()
    selected_request = request_response.data[0]

    if not request_response.data:
        abort(404, description="Request not found.")
    
    # Create the response and add CORS headers manually
    response = jsonify(selected_request)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    return response

@app.route("/request/<request_id>/approve", methods=['PUT', 'POST'])
def request_approve(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]
    result_reason = request.json.get('result_reason')  # Get result_reason from request body
    approved_dates = request.json.get("approved_dates")  # Get approved dates from the request
    print(access_token, result_reason, approved_dates)

    # Retrieve the request to be approved
    request_response = supabase.table("request").select("*").eq("request_id", request_id).execute()
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

    response = supabase.table("request").update({
        "status": 1,  # Approved status
        "result_reason": result_reason  # Store the result_reason
    }).eq("request_id", request_id).execute()

    if not response.data:
        abort(404, description="Request not found.")

    response = jsonify({"message": "Request approved successfully"})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Add CORS header
    return response

@app.route("/request/<request_id>/reject", methods=['PUT'])
def request_reject(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]
    result_reason = request.json.get('result_reason')  # Get result_reason from request body
    print(access_token, result_reason)

    response = supabase.table("request").update({
        "status": -1,  # Rejected status
        "result_reason": result_reason  # Store the result_reason
    }).eq("request_id", request_id).execute()

    if not response.data:
        abort(404, description="Request not found.")

    return {"message": "Request rejected successfully"}

@app.route("/getstaffid", methods=['GET'])
def get_staff_id():
    staff_id = request.headers.get('X-Staff-ID')
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    return {"message": "CORS is working", "staff_id": staff_id, "access_token": access_token}

@app.route("/requests/", methods=['POST'])
def create_request():
    form_data = request.json
    print(form_data)
    # Validate input
    if not form_data:
        return jsonify({"error": "No request data provided"}), 400
    try:
        # Insert new request into the Supabase database
        response = supabase.table("request").insert({
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
            app.logger.error("Database insert error: %s", response.status_code)
            return jsonify({"error": "Failed to insert data into the database"}), 500

        # If everything is fine, return the inserted request with a 201 status
        return jsonify(response.data[0]), 201
    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route("/requests/<int:staff_id>", methods=['GET'])
def get_requests_by_staff(staff_id: int):
    try:
        # Retrieve requests for the specified staff_id from the Supabase database
        response = supabase.table("request").select("*").eq("staff_id", staff_id).execute()
        print(response)
        # Check for errors in the response
        if response == None:
            app.logger.error("Database query error: %s", response["error"]["message"])
            return jsonify({"error": response["error"]["message"]}), 500
        
        # If no requests found, return a 404
        if response.data == []:
            return jsonify({"error": "No requests found for this staff ID"}), 404

        # Return the retrieved requests with a 200 status
        return jsonify(response.data), 200

    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0")