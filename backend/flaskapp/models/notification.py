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
            return selected_request

        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return employee
        
        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        email += f"Hi {staffname}, your request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]} has been partially or fully approved. Please check your schedule for details."
        return email
    
    def compose_reject(self, request_id):
        email = ""

        #get request data
        selected_request, status = self.supabase_caller.get_request_data(request_id)
        if int(status) != 200:
            return selected_request

        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return employee
        
        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        email += f"Hi {staffname}, your request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]} has been rejected."
        return email

    def compose_create(self):
        email = ""

        #get request data
        selected_request, status = self.supabase_caller.get_latest_req()
        if int(status) != 200:
            return selected_request
        
        #get staff data
        staffid = selected_request["staff_id"]
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return employee

        #get manager data
        managerid = employee["Reporting_Manager"]
        manager, status = self.supabase_caller.get_manager_data(managerid)
        if int(status) != 200:
            return manager

        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
        email += f"Hi {managername}, {staffname} has sent a request (ID: {selected_request["request_id"]}) from {selected_request["startdate"]} to {selected_request["enddate"]}. Please check requests for details."
        return email
    
    def compose_cancel(self, data):
        email = ""
        staffid = data["staff_id"]
        
        #get staff data
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return employee

        #get manager data
        managerid = employee["Reporting_Manager"]
        manager, status = self.supabase_caller.get_manager_data(managerid)
        if int(status) != 200:
            return manager

        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
        email += f"Hi {managername}, {staffname} has cancelled a request (ID: {data["request_id"]}) from {data["startdate"]} to {data["enddate"]}. Please check requests for details."
        return email

    def compose_withdraw(self, data):
        email = ""
        staffid = data["staff_id"]
        
        #get staff data
        employee, status = self.supabase_caller.get_staff_data(staffid)
        if int(status) != 200:
            return employee

        #get manager data
        managerid = employee["Reporting_Manager"]
        manager, status = self.supabase_caller.get_manager_data(managerid)
        if int(status) != 200:
            return manager

        #compose
        staffname = employee["Staff_FName"] + " " + employee["Staff_LName"]
        managername = manager["Staff_FName"] + " " + manager["Staff_LName"]
        email += f"Hi {managername}, {staffname} has withdrawn a request (ID: {data["request_id"]}) from {data["startdate"]} to {data["enddate"]}. Please check requests for details."
        return email
    
class notification_sender:
    def __init__(self, notif_engine):
        self.notif_engine = notif_engine
    
    def send_approve(self, request_id):
        email = self.notif_engine.compose_approve(request_id)
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code

    
    def send_reject(self, request_id):
        email = self.notif_engine.compose_reject(request_id)
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code
    
    def send_create(self):
        email = self.notif_engine.compose_create()
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code

    def send_withdraw(self, data):
        email = self.notif_engine.compose_withdraw(data)
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code
    
    def send_cancel(self, data):
        email = self.notif_engine.compose_cancel(data)
        data = {
            "TopicArn": topic,
            "Message": email
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code
    
    def send_test(self):
        data = {
            "TopicArn": topic,
            "Message": "email"
        }
        response = requests.post(sns_url, 
                      data=data
                     )
        return response.status_code

        

