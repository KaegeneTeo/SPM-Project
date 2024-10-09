from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request
from flask_cors import CORS
app = Flask(__name__)
CORS(app, credentials=True ,resources={r"/*": {
    "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID"]}})  # Enable CORS for frontend origin



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def test():
    return "Hello world", 200

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
        staff_response = supabase.table("Employee").select("Staff_ID").ilike("Email", json_response["email"]).execute()
        # print(staff_response.data[0]["Staff_ID"])
        if staff_response.data:
            json_response["staff_id"] = staff_response.data[0]["Staff_ID"]
        else:
            json_response["staff_id"] = None  # Or handle as needed


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
        raise HTTPException(status_code=404, detail="No team found for the logged-in user.")

    # Retrieve Staff_ID(s) of staff belonging to the team(s) of current logged in user
    staff_ids_response = supabase.table("team").select("staff_id").in_("team_id", team_ids).execute()
    
    staff_ids = [staff['staff_id'] for staff in staff_ids_response.data]
    print("Retrieved staff_ids:", staff_ids)
    
    # Throw error if no staff members are found
    if not staff_ids:
        raise HTTPException(status_code=404, detail="No staff found for the provided team IDs.")
    
    # Retrieve all requests of staff belonging to team(s) of logged in user
    requests_response = supabase.table("request").select("*").in_("staff_id", staff_ids).execute()
    
    requests = requests_response.data
    print("Retrieved requests:", requests)
    
    # Check if requests are found, else throw an error message
    if not requests:
        raise HTTPException(status_code=404, detail="No requests found for staff members in these teams.")
    
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
        raise HTTPException(status_code=404, detail="Request not found.")
    
    # Create the response and add CORS headers manually
    response = jsonify(selected_request)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    return response

@app.route("/request/<request_id>/approve", methods=['PUT'])
def request_approve(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(access_token)
    response = supabase.table("request").update({"status": 1}).eq("request_id", request_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Request not found.")
    
    return {"message": "Request approved successfully"}

@app.route("/request/<request_id>/reject", methods=['PUT'])
def request_reject(request_id):
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(access_token)
    response = supabase.table("request").update({"status": -1}).eq("request_id", request_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Request not found.")
    
    return {"message": "Request rejected successfully"}

if __name__ == '__main__':
    app.run(host="0.0.0.0")