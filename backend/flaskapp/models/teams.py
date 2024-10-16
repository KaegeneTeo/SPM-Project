from flask import jsonify, request, abort

class TeamsService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_staff_by_department(self, department):
        staff_query = self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, Reporting_Manager')
        if department == "CEO":
            staff_query = staff_query.eq("Position", 'Director')
        elif department != "All":
            staff_query = staff_query.eq("Dept", department)
        response = staff_query.execute()
        return response.data

    def get_manager_name(self, manager_id):
        manager_response = self.supabase.from_('Employee').select('Staff_FName, Staff_LName').eq('Staff_ID', manager_id).execute()
        print(manager_response)
        if manager_response.data:
            manager_fname = manager_response.data[0]['Staff_FName']
            manager_lname = manager_response.data[0]['Staff_LName']
            manager_name = f"{manager_fname} {manager_lname}"
            return manager_name
        return "Unknown"
    
    def get_team_by_manager_dept(self, manager_fname, manager_lname, dept):
        response = self.supabase.from_('Employee').select('Staff_ID').eq("Staff_FName", manager_fname).eq("Staff_LName", manager_lname).eq("Dept", dept ).execute()
        return response.data
    

    def get_team_ids_for_staff(self, staff_id):
        team_ids_response = self.supabase.from_("team").select("team_id").eq("staff_id", staff_id).execute()
        return [team['team_id'] for team in team_ids_response.data]

    def get_staff_in_teams(self, team_ids, staff_id):
        staff_ids_response = self.supabase.from_("team").select("staff_id").in_("team_id", team_ids).neq("staff_id", staff_id).execute()
        return [staff['staff_id'] for staff in staff_ids_response.data]

    def get_requests_for_staff(self, staff_ids):
        requests_response = self.supabase.from_("request").select("*").in_("staff_id", staff_ids).eq("status", 0).execute()
        return requests_response.data


class TeamsController:
    def __init__(self, teams_service):
        self.teams_service = teams_service

    def check_online(self):
        return "Hello teams", 200

    def get_team_details(self):
        manager_name = request.args.get('m_name')
        manager_fname = manager_name.split(" ")[0]
        manager_lname = manager_name.split(" ")[1]
        dept = request.args.get('dept')
        response = self.teams_service.get_team_by_manager_dept(manager_fname, manager_lname, dept)
        # print(response.data[0]["Staff_ID"])
        if manager_name and dept:
            return jsonify({"staff_id": response.data[0]["Staff_ID"]})
        else:
            return jsonify({"error": "No or wrong params received"}), 404

    def get_teams_by_reporting_manager(self):
        department = request.args.get('department')
        
        staff_data = self.teams_service.get_staff_by_department(department)
        if not staff_data:
            return jsonify({"error": "No staff found"}), 404
        
        positions_set = set(item['Position'] for item in staff_data)
        positions_list = list(positions_set)

        teams_by_manager = {}
        for item in staff_data:
            manager_id = item['Reporting_Manager']
            staff_id = item['Staff_ID']
            staff_fname = item['Staff_FName']
            staff_lname = item['Staff_LName']
            position = item['Position']

            if manager_id not in teams_by_manager:
                manager_name = self.teams_service.get_manager_name(manager_id)
                teams_by_manager[manager_id] = {
                    "manager_name": manager_name,
                    "teams": {}
                }

            if position not in teams_by_manager[manager_id]["teams"]:
                teams_by_manager[manager_id]["teams"][position] = []

            teams_by_manager[manager_id]["teams"][position].append({
                "staff_id": staff_id,
                "staff_fname": staff_fname,
                "staff_lname": staff_lname
            })

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

        dropdown_values = []
        for manager in result:
            for position in manager["positions"]:
                # Format the dropdown value as "Manager's Team (Position)"
                dropdown_value = f"{manager['manager_name']}'s Team ({position['position']})"
                dropdown_values.append(dropdown_value)

        return jsonify({
            "positions": positions_list,  # Include the list of unique positions
            "teams": result,              # Include the structured team info
            "dropdown_values": dropdown_values
        }), 200

    def get_team_requests(self):
        staff_id = request.headers.get('X-Staff-ID')
        if not staff_id:
            abort(400, description="Staff ID is required")
        
        team_ids = self.teams_service.get_team_ids_for_staff(staff_id)
        if not team_ids:
            abort(404, description="No team found for the logged-in user.")
        
        staff_ids = self.teams_service.get_staff_in_teams(team_ids, staff_id)
        if not staff_ids:
            abort(404, description="No staff found for the provided team IDs.")
        
        requests = self.teams_service.get_requests_for_staff(staff_ids)
        return jsonify(requests), 200
