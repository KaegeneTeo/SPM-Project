class notification_engine:
    #init
    def __init__(self, supabase):
        self.supabase = supabase
    
    #compose email on accepted schedule
    def compose_on_accept(self, request_id):
        email = ""
        request_response = self.supabase.from_("request").select("*").eq("request_id", request_id).execute()

        if not request_response.data:
            return {"error": "Requests not found"}, 404

        selected_request = request_response.data[0]

        staffid = selected_request["staff_id"]

        employee_response = self.supabase.from_("Employee").select("*").eq("Staff_ID", staffid).execute()

        if not request_response.data:
            return {"error": "Employee not found"}, 404
        
        employee = employee_response.data[0]
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]

        email += f"Hi ${staffname}, your request (ID: ${selected_request["request_id"]}) from ${selected_request["startdate"]} to ${selected_request["enddate"]} has been partially or fully approved. Please check your schedule for details."

class notification_sender:
    def __init__(self, notif_engine):
        self.notif_engine = notif_engine
    
    def send_to_employee():
        return

        

