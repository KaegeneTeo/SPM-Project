from flask import Flask, jsonify, Blueprint, request, abort, current_app
from flask_supabase import Supabase
supabase_extension = Supabase()

schedules = Blueprint("schedules", __name__)

@schedules.route("/team_details", methods = ['GET'])
def get_team_detail():
    manager_name = request.args.get('m_name')
    manager_fname = manager_name.split(" ")[0]
    manager_lname = manager_name.split(" ")[1]
    dept = request.args.get('dept')
    response = supabase_extension.client.from_('Employee').select('Staff_ID').eq("Staff_FName", manager_fname).eq("Staff_LName", manager_lname).eq("Dept", dept ).execute()
    # print(response.data[0]["Staff_ID"])
    if manager_name and dept:
        return jsonify({"staff_id": response.data[0]["Staff_ID"]})
    else:
        return jsonify({"error": "No or wrong params received"}), 404

@schedules.route("/teams_by_reporting_manager", methods=['GET'])
def get_teams_by_reporting_manager():
    department = request.args.get('department')
    
    # Initial query to get staff details
    staff_query = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, Reporting_Manager')

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
        staff_lname = item['Staff_LName']
        position = item['Position']

        # Get the manager's full name if not already retrieved
        if manager_id not in teams_by_manager:
            manager_response = supabase_extension.client.from_('Employee').select('Staff_FName, Staff_LName').eq('Staff_ID', manager_id).execute()
            if manager_response.data:
                manager_fname = manager_response.data[0]['Staff_FName']
                manager_lname = manager_response.data[0]['Staff_LName']
                manager_name = f"{manager_fname} {manager_lname}"
            else:
                manager_name = "Unknown"
                
            teams_by_manager[manager_id] = {
                "manager_name": manager_name,
                "teams": {}  # Initialize an empty dict to hold positions and their team members
            }

        # Add staff member to the manager's team under the appropriate position
        if position not in teams_by_manager[manager_id]["teams"]:
            teams_by_manager[manager_id]["teams"][position] = []

        teams_by_manager[manager_id]["teams"][position].append({
            "staff_id": staff_id,
            "staff_fname": staff_fname,
            "staff_lname": staff_lname
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

    # Prepare the dropdown values
    dropdown_values = []
    for manager in result:
        for position in manager["positions"]:
            # Format the dropdown value as "Manager's Team (Position)"
            dropdown_value = f"{manager['manager_name']}'s Team ({position['position']})"
            dropdown_values.append(dropdown_value)

    # Return the result in the desired format
    return jsonify({
        "positions": positions_list,  # Include the list of unique positions
        "teams": result,              # Include the structured team info
        "dropdown_values": dropdown_values  # Include the formatted dropdown values
    }), 200


@schedules.route("/schedules", methods=['GET'])
def get_schedules():

    #getting CEO for director tram filter cuz director is a cross dept team while all other teams are within dept so this needs special logic, also did you know that you can put emojis in comments and variable names? 😁
    CEO = int(supabase_extension.client.from_('Employee').select('Staff_ID').eq("Position", "MD").execute().data[0]["Staff_ID"])

    #get data & print for debug
    data = request.args
    print(data)
    
    #filters

    #filter for all depts
    if data["dept"] == "all":
        allnames = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').execute()
        response = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').execute()
    #filter for all teams in dept
    elif data["reporting_manager"] == "all":
        allnames = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).execute()
        response = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", data["dept"]).execute()
    
    #special logic for filtering by CEO dept
    elif data["dept"] == "CEO":
        allnames = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).execute()
        response = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", data["dept"]).execute()

    #get director team (special logic mentioned earlier)
    elif int(data["role"]) == 1 and int(data['reporting_manager']) == CEO:
        allnames = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).neq("Dept", "CEO").execute()
        response = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Reporting_Manager", data["reporting_manager"]).neq("Dept", "CEO").execute()
    
    #filter for dept and team
    else:
        allnames = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName').eq("Dept", data["dept"]).eq("Reporting_Manager", int(data["reporting_manager"])).execute()
        response = supabase_extension.client.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", data["dept"]).eq("Reporting_Manager", int(data["reporting_manager"])).execute()
    
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