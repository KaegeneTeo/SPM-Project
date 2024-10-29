class SchedulesService:
    def __init__(self, supabase):
        self.supabase = supabase

    
    def get_own_schedule(self,staff_id):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)').eq('Staff_ID', staff_id).execute()
    
    #for special logic for CEO and directors
    def get_ceo(self):
        return int(self.supabase.from_('Employee').select('Staff_ID').eq("Position", "MD").execute().data[0]["Staff_ID"])

    #for all depts filter
    def get_all_employees(self):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position').execute()

    def get_schedules_for_all_depts(self):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)').execute()

    #for dept specified, all teams filter
    def get_all_employees_by_dept(self, dept):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position').eq("Dept", dept).execute()
    
    def get_schedules_by_dept(self, dept):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", dept).execute()

    #for teams filter
    def get_schedules_by_reporting_manager(self, dept, reporting_manager):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Dept", dept).eq("Reporting_Manager", reporting_manager).execute()

    def get_all_employees_by_reporting_manager(self, dept, reporting_manager):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position').eq("Dept", dept).eq("Reporting_Manager", reporting_manager).execute()
    
    #for directors team
    def get_all_directors(self, reporting_manager):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position').eq("Reporting_Manager", reporting_manager).neq("Postion", "MD").execute()
    
    def get_directors_schedules(self, reporting_manager):
        return self.supabase.from_('Employee').select('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)').eq("Reporting_Manager", reporting_manager).neq("Postion", "MD").execute()
    
    #for data transform
    def format_schedules(self, response, allnames):
        try:
            responselist = list(response.data)
        except:
            return {"code": 404, "message": "No data or bad data"}, 404

        # Process the schedule data
        schedulelist = []
        for i in range(len(responselist)):
            for j in range(len(responselist[i]["schedule"])):
                schedulelist.append({
                    "dept": responselist[i]["Dept"],
                    "staff_fname": responselist[i]["Staff_FName"],
                    "staff_lname": responselist[i]["Staff_LName"],
                    "date": responselist[i]["schedule"][j]["date"],
                    "schedule_id": responselist[i]["schedule"][j]["schedule_id"],
                    "time_slot": responselist[i]["schedule"][j]["time_slot"],
                    "staff_id": responselist[i]["Staff_ID"],
                    "position": responselist[i]["Position"],
                    "dept": responselist[i]["Dept"]
                })

        # Compress the list of schedules to create a NameList for each datetime
        dict1 = {}
        for item in schedulelist:
            temp = {
                "Date": item["date"],
                "Time_Slot": item["time_slot"],
                "Name_List": [f'{item["staff_id"]} - {item["staff_fname"]} {item["staff_lname"]} - {item["dept"]} - {item["position"]}']
            }
            if (item["date"], item["time_slot"]) not in dict1:
                dict1[(item["date"], item["time_slot"])] = temp
            else:
                dict1[(item["date"], item["time_slot"])]["Name_List"].append(f'{item["staff_id"]} - {item["staff_fname"]} {item["staff_lname"]} - {item["dept"]} - {item["position"]}')

        # Convert data into the final format for frontend
        returnlist = []
        allnamelist = [f'{employee["Staff_ID"]} - {employee["Staff_FName"]} {employee["Staff_LName"]} - {employee["Dept"]} - {employee["Position"]}' for employee in allnames.data]

        for key in dict1:
            time_slot_data = dict1[key]
            time_slot_label = "AM" if time_slot_data["Time_Slot"] == 1 else "PM"
            time_start = f'{time_slot_data["Date"]} 09:00' if time_slot_label == "AM" else f'{time_slot_data["Date"]} 14:00'
            time_end = f'{time_slot_data["Date"]} 13:00' if time_slot_label == "AM" else f'{time_slot_data["Date"]} 18:00'
            in_office = [employee for employee in allnamelist if employee not in time_slot_data["Name_List"]]

            returnlist.append({
                "start": time_start,
                "end": time_end,
                "class": time_slot_label,
                "WFH": time_slot_data["Name_List"],
                "count": len(time_slot_data["Name_List"]),
                "title": len(time_slot_data["Name_List"]),
                "inOffice": in_office
            })
        # print(returnlist)
        return {"schedules": returnlist}, 200
