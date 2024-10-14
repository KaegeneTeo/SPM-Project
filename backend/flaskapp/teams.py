from flask import Flask, jsonify, Blueprint, request, abort, current_app
from datetime import datetime, timedelta
from flask_supabase import Supabase
supabase_extension = Supabase()
team = Blueprint("team", __name__)

@team.route("/teams", methods=['GET'])
def check_online():
    return "Hello teams", 200


@team.route("/teams_by_reporting_manager", methods=['GET'])
def get_teams_by_reporting_manager():
    department = request.args.get('department')
    
    # Initial query to get staff details
    staff_query = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Dept, Position, Reporting_Manager')

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
            manager_response = supabase_extension.client.from_('Employee').select('Staff_FName').eq('Staff_ID', manager_id).execute()
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


@team.route('/team/requests', methods=['GET'])
def get_team_requests():
    staff_id = request.headers.get('X-Staff-ID')
    access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
    print(staff_id, access_token)
    
    # Retrieve Team_ID(s) of current logged in user and store in list
    team_ids_response = supabase_extension.client.from_("team").select("team_id").eq("staff_id", staff_id).execute()
    team_ids = [team['team_id'] for team in team_ids_response.data]
    print("Retrieved team_ids:", team_ids)

    # Throw error if no team_ids
    if not team_ids:
        abort(404, description="No team found for the logged-in user.")

    # Retrieve Staff_ID(s) of staff belonging to the team(s) of the current logged-in user
    staff_ids_response = supabase_extension.client.from_("team").select("staff_id").in_("team_id", team_ids).neq("staff_id", staff_id).execute()
    
    staff_ids = [staff['staff_id'] for staff in staff_ids_response.data]
    print("Retrieved staff_ids:", staff_ids)
    
    # Throw error if no staff members are found
    if not staff_ids:
        abort(404, description="No staff found for the provided team IDs.")
    
    # Retrieve all requests of staff belonging to team(s) of logged in user where status = 0
    requests_response = supabase_extension.client.from_("request").select("*").in_("staff_id", staff_ids).eq("status", 0).execute()
    
    requests = requests_response.data
    print("Retrieved requests:", requests)
    
    # Create the response and add CORS headers manually
    response = jsonify(requests)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    return response