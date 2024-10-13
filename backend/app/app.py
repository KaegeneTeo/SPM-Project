from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request, abort
from flask_cors import CORS
from datetime import datetime, timedelta
app = Flask(__name__)
CORS(app, credentials=True ,resources={r"/*": {
    "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
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

    for date in dates:
        response = supabase.table("schedule").insert({
            "staff_id": staff_id,
            "date": date,
            "time_slot": time_slot
        }).execute()

        if response == None:
            app.logger.error("Failed to create schedule entry for date %s: %s", date, response)

# Routes
@app.route("/")
def test():
    return "Hello world", 200

@app.route("/teams_by_reporting_manager", methods=['GET'])
def get_teams_by_reporting_manager():
    department = request.args.get('department')
    
    # Initial query to get staff details
    staff_query = supabase.from_('Employee').select('Staff_ID, Staff_FName, Dept, Position, Reporting_Manager')

    # If department is 'CEO', filter by 'Director' position
    if department == "CEO":
        staff_query = staff_query.eq("Position", 'Director')
        
    # Filter based on department if specified (excluding CEO case)
    elif department != "All":
        staff_query = staff_query.eq("Dept", department)

    # Execute the query
    response = staff_query.execute()

    if not response.data:
        return jsonify({"error": "No staff found"}), 404

    # Get unique positions in the department
    positions_set = set(item['Position'] for item in response.data)
    positions_list = list(positions_set)

    # Group staff by reporting manager and position
    teams_by_manager = {}
    for item in response.data:
        manager_id = item['Reporting_Manager']
        staff_id = item['Staff_ID']
        staff_fname = item['Staff_FName']
        position = item['Position']

        # Get the manager's full name if not already retrieved
        if manager_id not in teams_by_manager:
            manager_response = supabase.from_('Employee').select('Staff_FName').eq('Staff_ID', manager_id).execute()
            manager_name = manager_response.data[0]['Staff_FName'] if manager_response.data else "Unknown"
            teams_by_manager[manager_id] = {
                "manager_name": manager_name,
                "teams": {}  # Initialize an empty dict to hold positions and their team members
            }

        # Add staff member to the manager's team under the appropriate position
        if position not in teams_by_manager[manager_id]["teams"]:
            teams_by_manager[manager_id]["teams"][position] = []

        teams_by_manager[manager_id]["teams"][position].append({
            "staff_id": staff_id,
            "staff_fname": staff_fname
        })

    # Format the results to send to the frontend
    result = []
    for manager_id, info in teams_by_manager.items():
        manager_info = {
            "manager_id": manager_id,
            "manager_name": info["manager_name"],
            "positions": []
        }
        for position, team in info["teams"].items():
            manager_info["positions"].append({
                "position": position,
                "team": team
            })
        result.append(manager_info)

    print(result)  # Print the structured result for debugging

    # Check if result is empty and handle accordingly
    if len(result) == 0:
        return jsonify({"positions": positions_list, "teams": []}), 200

    # Return the result in the desired format
    return jsonify({
        "positions": positions_list,  # Include the list of unique positions
        "teams": result  # Include the structured team info
    }), 200

@app.route("/schedules", methods=['GET'])
def get_schedules():

    #getting CEO for director tram filter cuz director is a cross dept team while all other teams are within dept so this needs special logic, also did you know that you can put emojis in comments and variable names? 😁
    CEO = int(supabase.from_('Employee').select('Staff_ID').eq("Position", "MD").execute().data[0]["Staff_ID"])

    #get data & print for debug
    data = request.args
    print(data)
    
    #filters

    #filter for all depts
    if data["dept"] == "all":
        allnames = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').execute()
        response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').execute()
    #filter for all teams in dept
    elif data["reporting_manager"] == "all":
        allnames = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).execute()
        response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", data["dept"]).execute()
    
    #get director team (special logic mentioned earlier)
    elif int(data["role"]) == 1 and int(data['reporting_manager']) == CEO:
        response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Reporting_Manager", data["reporting_manager"]).execute()
    
    #filter for dept and team
    else:
        allnames = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).eq("Reporting_Manager", int(data["reporting_manager"])).execute()
        response = supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", data["dept"]).eq("Reporting_Manager", int(data["reporting_manager"])).execute()
    
    #I forgor💀 what this is for but assumedly I ran into a bug at some point with bad output from db, unsure if it still exists but better safe than sorry
    try:
        responselist = list(response.data)
    except:
        return jsonify({"code":404,
                       "message": "No data or bad data"})
    else:
    # removing nested list in the data return format for easier processing
        schedulelist = []
        for i in range(0, len(responselist)):
            for j in range(0, len(responselist[i]["schedule"])):
                schedulelist.append({
                    "dept" : responselist[i]["Dept"],
                    "staff_fname" : responselist[i]["Staff_FName"],
                    "staff_lname" : responselist[i]["Staff_LName"],
                    "date" : responselist[i]["schedule"][j]["date"],
                    "schedule_id" : responselist[i]["schedule"][j]["schedule_id"],
                    "time_slot" : responselist[i]["schedule"][j]["time_slot"],
                    "staff_id" : responselist[i]["Staff_ID"]
                })
    #compressing list of schedules to create NameList of wfh for each datetime, aka changing keys from staff_id to timeslot & date 
        dict1 = {}
        for i in range(0, len(schedulelist)):
            temp = {
                "Date": schedulelist[i]["date"],
                "Time_Slot": schedulelist[i]["time_slot"],
                "Name_List": [str(schedulelist[i]["staff_id"]) + " - " + schedulelist[i]["staff_fname"] + " " + schedulelist[i]["staff_lname"]]
                }
            if dict1.get((schedulelist[i]["date"], schedulelist[i]["time_slot"])) == None:
                dict1[(schedulelist[i]["date"], schedulelist[i]["time_slot"])] = temp
            else:
                dict1[(schedulelist[i]["date"], schedulelist[i]["time_slot"])]["Name_List"].append(str(schedulelist[i]["staff_id"]) + " - " + schedulelist[i]["staff_fname"] + " " + schedulelist[i]["staff_lname"])
    #converting data into final return format to work with vuecal + appending inOffice list for display using allnames list 
        returnlist = []
        allnamelist = [str(employee["Staff_ID"]) + " - " + employee["Staff_FName"] + " " + employee["Staff_LName"] for employee in list(allnames.data)]
        for key in list(dict1.keys()):
            if dict1[key]["Time_Slot"] == 1:
                returnlist.append({
                "start": str(dict1[key]["Date"]) + " 09:00",
                "end": str(dict1[key]["Date"]) + " 13:00",
                "class": "AM",
                "WFH": dict1[key]["Name_List"],
                "count" : str(len(dict1[key]["Name_List"])),
                "title": len(dict1[key]["Name_List"]),
                "inOffice" : [employee for employee in allnamelist if employee not in dict1[key]["Name_List"]]
                })
            if dict1[key]["Time_Slot"] == 2:
                returnlist.append({
                "start": str(dict1[key]["Date"]) + " 14:00",
                "end": str(dict1[key]["Date"]) + " 18:00",
                "class": "PM",
                "WFH": dict1[key]["Name_List"],
                "count" : str(len(dict1[key]["Name_List"])),
                "title": len(dict1[key]["Name_List"]),
                "inOffice" : [employee for employee in allnamelist if employee not in dict1[key]["Name_List"]]
                })
    #return in json
        return jsonify({"schedules": returnlist})


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
        staff_response = supabase.table("Employee").select("Staff_ID, Role, Dept, Reporting_Manager").ilike("Email", json_response["email"]).execute()
        
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
    
    # Retrieve all requests of staff belonging to team(s) of logged in user where status = 0
    requests_response = supabase.table("request").select("*").in_("staff_id", staff_ids).eq("status", 0).execute()
    
    requests = requests_response.data
    print("Retrieved requests:", requests)
    
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