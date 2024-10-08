from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request
from flask_cors import CORS
app = Flask(__name__)
CORS(app, credentials=True ,resources={r"/*": {"origins": "http://localhost:5173"}})  # Enable CORS for frontend origin



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
        staff_response = supabase.table("Employee").select("Staff_ID").eq("Email", json_response["email"]).execute()
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




# @app.route("/team/requests", methods=['GET'])
# def get_requests_for_teams():
#     # Get all team_ids from the session
#     print("Request received!")
#     session = await supabase.auth.get_session()
#     print(session)
#     user_staff_id = session['data']['session']['user']['staff_id']  
#     print("Extracted staff_id:", staff_id)

#     # Get team ID(s) of logged in user by staff ID using get_team_ids_by_staff Supabase function 
#     team_ids_response = await supabase.rpc("get_team_ids_by_staff", {'staff_id': staff_id}).execute()
#     print(team_ids_response)

#     if team_ids_response.get("error"):
#         raise HTTPException(status_code=500, detail="Error fetching team IDs: " + team_ids_response["error"])

#     team_ids = [team['team_id'] for team in team_ids_response.data]
#     print("Retrieved team_ids:", team_ids)

#     # Throw error if no team_ids
#     if not team_ids:
#         raise HTTPException(status_code=404, detail="No team found for the logged-in user.")

#     # Retrieve all staff IDs using get_staff_ids_by_team Supabase function
#     staff_ids_response = supabase.rpc('get_staff_ids_by_team', {'team_ids': team_ids}).execute()
#     print(staff_ids_response)

#     if staff_ids_response.get("error"):
#         raise HTTPException(status_code=500, detail="Error fetching staff IDs: " + staff_ids_response["error"])
    
#     staff_ids = [staff['staff_id'] for staff in staff_ids_response.data]
#     print(staff_ids)
    
#     # Throw error if no staff members are found
#     if not staff_ids:
#         raise HTTPException(status_code=404, detail="No staff found for the provided team IDs.")
    
#     # Get all requests for the list of staff IDs using get_requests_by_staff_ids Supabase function
#     requests_response = supabase.rpc('get_requests_by_staff_ids', {'staff_ids': staff_ids}).execute()
#     print(requests_response)
    
#     if requests_response.get("error"):
#         raise HTTPException(status_code=500, detail="Error fetching requests: " + requests_response["error"])
    
#     requests = requests_response.data
#     print(requests)
    
#     # Check if requests are found, else throw an error message
#     if not requests:
#         raise HTTPException(status_code=404, detail="No requests found for staff members in these teams.")
    
#     # Return the retrieved requests
#     return jsonable_encoder(requests)

if __name__ == '__main__':
    app.run(host="0.0.0.0")