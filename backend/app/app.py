from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request, abort
from flask_cors import CORS
app = Flask(__name__)
CORS(app, credentials=True ,resources={r"/*": {
    "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role"]}})  # Enable CORS for frontend origin



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def test():
    return "Hello world", 200

@app.route("/schedules", methods=['GET'])
def get_schedules():
    data = request.json
    keys = list(data.keys())
    dict1 = {}
    if "ID" in keys:
        allnames = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName').eq("STAFF_ID", data["ID"]).execute()
        response = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName, Dept, schedule(Schedule_ID, Staff_ID, Date, Time_Slot)').eq("STAFF_ID", data["ID"]).execute()
    elif "Dept" in keys:
        if "Team" in keys:
            allnames = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName').eq("Team", data["Team"]).eq("Dept", data["Dept"]).execute()
            response = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName, Dept, schedule(Schedule_ID, Staff_ID, Date, Time_Slot)').eq("Team", data["Team"]).eq("Dept", data["Dept"]).execute()  
        else:
            allnames = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName').eq("Dept", data["Dept"]).execute()
            response = supabase.from_('employees').select('STAFF_ID, Staff_FName, Staff_LName, Dept, schedule(Schedule_ID, Staff_ID, Date, Time_Slot)').eq("Dept", data["Dept"]).execute()  
    responselist = list(response.data)
    for i in range(0, len(responselist)):
        dict1 = dict1.get((responselist[i]["Date"], responselist[i]["Time_Slot"]), {
            "Date": responselist[i]["Date"],
            "Time_Slot": responselist[i]["Time_Slot"],
            "Name_List": list(responselist[i]["STAFF_ID"] + " - " + responselist[i]["STAFF_FName"] + " " + responselist[i]["STAFF_LName"])
            })["Name_List"].append(responselist[i]["STAFF_ID"] + " - " + responselist[i]["STAFF_FName"] + " " + responselist[i]["STAFF_LName"])
    dict2 = {}
    for key, value in dict1.items():
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
        staff_response = supabase.table("Employee").select("Staff_ID, Role").ilike("Email", json_response["email"]).execute()
        print(staff_response.data)
        if staff_response.data:
            json_response["staff_id"] = staff_response.data[0]["Staff_ID"]
            json_response["role"] = staff_response.data[0]["Role"]
        else:
            json_response["staff_id"] = None  # Or handle as needed
            json_response["role"] = None

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

@app.route("/request/<request_id>/approve", methods=['PUT'])
def request_approve(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]
    result_reason = request.json.get('result_reason')  # Get result_reason from request body
    print(access_token, result_reason)

    response = supabase.table("request").update({
        "status": 1,  # Approved status
        "result_reason": result_reason  # Store the result_reason
    }).eq("request_id", request_id).execute()

    if not response.data:
        abort(404, description="Request not found.")

    return {"message": "Request approved successfully"}

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