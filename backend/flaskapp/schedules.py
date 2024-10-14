from flask import Flask, jsonify, Blueprint, request, abort, current_app
from flask_supabase import Supabase
supabase_extension = Supabase()

schedule = Blueprint("schedule", __name__)

#?dept=Sales&role=1&position=Director&reporting_manager=all
@schedule.route("/schedules", methods=['GET'])
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