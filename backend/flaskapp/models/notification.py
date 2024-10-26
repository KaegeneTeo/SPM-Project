import requests
import os
from dotenv import load_dotenv
load_dotenv()

sns_url = os.environ.get("SNS_URL")
topic = os.environ.get("TOPIC")

class supabase_access:
    def __init__(self,supabase):
        self.supabase = supabase

    #get request data
    def get_request_data(self, request_id):
        request_response = self.supabase.from_("request").select("*").eq("request_id", request_id).execute()
        if not request_response.data:
            return {"error": "Requests not found"}, 404
        selected_request = request_response.data[0]
        return selected_request, 200

    #get staff data
    def get_staff_data(self, staffid):
        employee_response = self.supabase.from_("Employee").select("*").eq("Staff_ID", staffid).execute()
        if not employee_response.data:
            return {"error": "Employee not found"}, 404
        employee = employee_response.data[0]
        return employee, 200
    
    #get latest req
    def get_latest_req(self):
        request_response = self.supabase.from_("request").select("*").order('request_id', desc=True).limit(1).execute()
        if not request_response.data:
            return {"error": "Requests not found"}, 404
        selected_request = request_response.data[0]
        return selected_request, 200

    #get manager data
    def get_manager_data(self, managerid):
        manager_response = self.supabase.from_("Employee").select("*").eq("Staff_ID", managerid).execute()
        if not manager_response.data:
            return {"error": "Employee not found"}, 404
        manager = manager_response.data[0]
        return manager, 200



class notification_engine:
    #init
    def __init__(self, supabase_access):
        self.supabase_caller = supabase_access
    
    #compose email on accepted schedule
    def compose_approve(self, request_id):
        email = ""

        #get request data
        selected_request, status = self.supabase_caller.get_request_data(request_id)
        if int(status) != 200:
            return "Error fetching request", 500

        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return "Error fetching staff", 500
        
        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        email += f"Hi {staffname}, your request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]} has been partially or fully approved. Please check your schedule for details."
        return email, 200
    
    def compose_reject(self, request_id):
        email = ""

        #get request data
        selected_request, status = self.supabase_caller.get_request_data(request_id)
        if int(status) != 200:
            return "Error fetching request", 500

        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return "Error fetching staff", 500
        
        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        email += f"Hi {staffname}, your request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]} has been rejected."
        return email, 200

    def compose_create(self):
        email = ""

        #get request data
        selected_request, status = self.supabase_caller.get_latest_req()
        if int(status) != 200:
            return "Error fetching request", 500
        
        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return "Error fetching staff", 500

        #get manager data
        managerid = employee["Reporting_Manager"]
        manager, status = self.supabase_caller.get_manager_data(managerid)
        if int(status) != 200:
            return "Error fetching manager", 500

        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
        email += f"Hi {managername}, {staffname} has sent a request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]}. Please check requests for details."
        return email, 200
    
    def compose_cancel(self, data):
        email = ""
        try:
            staffid = data["staff_id"]
        except:
            return "Erroneous arguments submitted", 500
        else:
            #get staff data
            employee, status = self.supabase_caller.get_staff_data(staffid)
            if int(status) != 200:
                return "Error fetching staff", 500

            #get manager data
            managerid = employee["Reporting_Manager"]
            manager, status = self.supabase_caller.get_manager_data(managerid)
            if int(status) != 200:
                return "Error fetching manager", 500

            #compose
            staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
            managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
            email += f"Hi {managername}, {staffname} has cancelled a request (ID: {data["request_id"]}) from {data["startdate"]} to {data["enddate"]}. Please check requests for details."
            return email, 200

    def compose_withdraw(self, data):
        email = ""
        try:
            staffid = data["staff_id"]
        except:
            return "Erroneous arguments submitted", 500
        else:
            #get staff data
            employee, status = self.supabase_caller.get_staff_data(staffid)
            if int(status) != 200:
                return "Error fetching staff", 500

            #get manager data
            managerid = employee["Reporting_Manager"]
            manager, status = self.supabase_caller.get_manager_data(managerid)
            if int(status) != 200:
                return "Error fetching manager", 500

            #compose
            staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
            managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
            email += f"Hi {managername}, {staffname} has withdrawn a request (ID: {data["request_id"]}) from {data["startdate"]} to {data["enddate"]}. Please check requests for details."
            return email, 200
    
class notification_sender:
    def __init__(self, notif_engine):
        self.notif_engine = notif_engine
    
    def send_approve(self, request_id):
        email, status = self.notif_engine.compose_approve(request_id)
        if int(status) == 500:
            return email
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        if response.status_code != 200:
            return "Email failed to send"
        return response.status_code

    
    def send_reject(self, request_id):
        email, status = self.notif_engine.compose_reject(request_id)
        if int(status) == 500:
            return email
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        if response.status_code != 200:
            return "Email failed to send"
        return response.status_code
    
    def send_create(self):
        email, status = self.notif_engine.compose_create()
        if int(status) == 500:
            return email
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        if response.status_code != 200:
            return "Email failed to send"
        return response.status_code

    def send_withdraw(self, data):
        email, status = self.notif_engine.compose_withdraw(data)
        if int(status) == 500:
            return email
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        if response.status_code != 200:
            return "Email failed to send"
        return response.status_code
    
    def send_cancel(self, data):
        email, status = self.notif_engine.compose_cancel(data)
        if int(status) == 500:
            return email
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        if response.status_code != 200:
            return "Email failed to send"
        return response.status_code

        

