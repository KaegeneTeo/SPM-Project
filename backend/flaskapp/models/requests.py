from flask import request, abort, current_app
from datetime import datetime, timedelta

class RequestService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def withdraw_request(self, request_id):
        try:
            data = self.supabase.from_("request").select().eq("request_id", request_id).execute()
            staff_id = data.data[0]['staff_id']
            startdate = data.data[0]['startdate']
            enddate = data.data[0]['enddate']
            response = self.supabase.from_("request").delete().eq("request_id", request_id).execute()
            
            if not response.data:
                abort(404, description="Request not found.")

            return {"message": "Request cancel successful", 
                    "data": {"request_id": request_id, "staff_id": staff_id, "startdate": startdate, "enddate": enddate}}, 200 

        except Exception as e:
            return {"error": str(e)}, 500

    def cancel_request(self, request_id):
        try:
            data = self.supabase.from_("request").select().eq("request_id", request_id).execute()
            staff_id = data.data[0]['staff_id']
            startdate = data.data[0]['startdate']
            enddate = data.data[0]['enddate']

            response = self.supabase.from_("request").delete().eq("request_id", request_id).execute()
            response2 = self.supabase.from_("schedule").delete().eq("request_id", request_id).execute()
            

            if not response.data or not response2.data:
                abort(404, description="Request not found.")

            return {"message": "Request withdrawn successful",
                    "data":{"request_id": request_id, "staff_id": staff_id, "startdate": startdate, "enddate": enddate}}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_staff_id(self):
        staff_id = request.headers.get('X-Staff-ID')
        authorization_header = request.headers.get('Authorization')
        
        if authorization_header and "Bearer " in authorization_header:
            access_token = authorization_header.split(' ')[1]  # Extract Bearer token
        else:
            access_token = None  # Handle missing or malformed Authorization header
        
        return {"message": "CORS is working", "staff_id": staff_id, "access_token": access_token}, 200

    def create_request(self, form_data):
        # Validate input
        if not form_data:
            return {"error": "No request data provided"}, 400
        try:
            # Insert new request into the Supabase database
            response = self.supabase.from_("request").insert({
                "staff_id": form_data.get('staffid'),
                "reason": form_data.get("reason"),
                "status": form_data.get("status"),
                "startdate": form_data.get("startdate"),
                "enddate": form_data.get("enddate"),
                "time_slot": form_data.get("time_slot"),
                "request_type": form_data.get("request_type"),
            }).execute()

            # Check for errors in the response
            if response is None:
                current_app.logger.error("Database insert error")
                return {"error": "Failed to insert data into the database"}, 500

            # If everything is fine, return the inserted request
            return response.data[0], 201
        except Exception as e:
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500

    def get_requests_by_staff(self, staff_id):
        try:
            # Retrieve requests for the specified staff_id from the Supabase database
            response = self.supabase.from_("request").select("*").eq("staff_id", staff_id).execute()

            # Check for errors in the response
            if response is None:
                current_app.logger.error("Database query error")
                return {"error": "Failed to retrieve data from the database"}, 500

            # If no requests found, return a 404
            if not response.data:
                return {"error": "No requests found for this staff ID"}, 404

            # Return the retrieved requests
            return response.data, 200
        except Exception as e:
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500
    
    def get_team_requests(self, staff_id):
        # Query for the current user's role and position based on staff_id
        user_response = self.supabase.from_('Employee').select('Role, Position').eq('Staff_ID', staff_id).execute()
        
        if not user_response.data:
            return {"error": "User not found"}, 404

        current_user = user_response.data[0]
        role = current_user['Role']
        position = current_user['Position'].lower()

        # Check if the user is eligible to view team requests (Role 1 or Role 3 + Manager/Director)
        if (role == 1 or role == 3) and ('manager' in position or 'director' in position):
            # Fetch the staff members who report to this Manager/Director from the Employee table
            response = self.supabase.from_('Employee').select('Staff_ID').eq('Reporting_Manager', staff_id).execute()

            if response.data:
                team_member_ids = [member['Staff_ID'] for member in response.data]

                # Retrieve requests of staff belonging to the logged-in user's team where status = 0
                requests_response = self.supabase.from_("request").select("*").in_("staff_id", team_member_ids).eq("status", 0).execute()
                return requests_response.data, 200
            else:
                return [], 404
        else:
            # User not authorized to view team requests
            return [], 401

    def get_selected_request(self, request_id):
        # Retrieve selected request by request_id
        request_response = self.supabase.from_("request").select("*").eq("request_id", request_id).execute()

        if not request_response.data:
            return {"error": "Request not found"}, 404

        selected_request = request_response.data[0]
        return selected_request, 200

    def calculate_recurring_dates(self, approved_dates):
        if not approved_dates:
            return []
        
        date_list = []
        earliest_date = min([datetime.strptime(date, '%Y-%m-%d') for date in approved_dates])
        end_date = earliest_date + timedelta(days=365)

        approved_weekdays = [date.weekday() for date in [datetime.strptime(date, '%Y-%m-%d') for date in approved_dates]]

        current_date = earliest_date
        while current_date <= end_date:
            if current_date.weekday() in approved_weekdays:
                date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return date_list

    def create_schedule_entries(self, staff_id, dates, time_slot, request_id):
        for date in dates:
            time_slot_int = int(time_slot) if isinstance(time_slot, (int, float, str)) and str(time_slot).isdigit() else time_slot
            
            if time_slot_int == 3:
                # Insert first record with time_slot as 1
                response1 = self.supabase.from_("schedule").insert({
                    "staff_id": staff_id,
                    "date": date,
                    "time_slot": 1,
                    "request_id": request_id
                }).execute()

                if response1 is None:
                    current_app.logger.error("Failed to create schedule entry for date %s with time_slot 1", date)

                # Insert second record with time_slot as 2
                response2 = self.supabase.from_("schedule").insert({
                    "staff_id": staff_id,
                    "date": date,
                    "time_slot": 2,
                    "request_id": request_id
                }).execute()

                if response2 is None:
                    current_app.logger.error("Failed to create schedule entry for date %s with time_slot 2", date)
            elif time_slot_int in [1, 2]:
                # Insert single record for other time_slot values
                response = self.supabase.from_("schedule").insert({
                    "staff_id": staff_id,
                    "date": date,
                    "time_slot": time_slot_int,
                    "request_id": request_id
                }).execute()

        # if response is None:
        #     current_app.logger.error("Failed to create schedule entry for date %s", date)

    def approve_request(self, request_id, result_reason, approved_dates):
        try:
            # Retrieve request data
            request_response = self.supabase.from_("request").select("*").eq("request_id", request_id).execute()

            if not request_response.data:
                abort(404, description="Request not found.")

            request_data = request_response.data[0]
            staff_id = request_data['staff_id']
            request_type = request_data['request_type']
            time_slot = request_data['time_slot']
            requestId = request_data['request_id']

            if request_type == 2:  # Recurring
                recurring_dates = self.calculate_recurring_dates(approved_dates)
                self.create_schedule_entries(staff_id, recurring_dates, time_slot, requestId)
            else:  # Ad-hoc
                self.create_schedule_entries(staff_id, approved_dates, time_slot, requestId)

            self.supabase.from_("request").update({
                "status": 1,  # Approved status
                "result_reason": result_reason
            }).eq("request_id", request_id).execute()

            return {"message": "Request approved successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def reject_request(self, request_id, result_reason):
        try:
            response = self.supabase.from_("request").update({
                "status": -1,  # Rejected status
                "result_reason": result_reason
            }).eq("request_id", request_id).execute()

            if not response.data:
                abort(404, description="Request not found.")

            return {"message": "Request rejected successfully"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


class RequestController:
    def __init__(self, request_service):
        self.request_service = request_service

    def withdraw_request(self, request_id):
        try:
            response_data, status_code = self.request_service.withdraw_request(request_id)
            return response_data, status_code
        except Exception as e:
            # Log the exception if needed
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500
    
    def cancel_request(self, request_id):
        try:
            response_data, status_code = self.request_service.cancel_request(request_id)
            return response_data, status_code
        except Exception as e:
            # Log the exception if needed
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500
    
    def get_staff_id(self):
        response_data, status_code = self.request_service.get_staff_id()
        return response_data, status_code

    def create_request(self):
        form_data = request.json
        try:
            response_data, status_code = self.request_service.create_request(form_data)
            return response_data, status_code
        except Exception as e:
            # Handle the exception and log the error
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500

    def get_requests_by_staff(self, staff_id):
        response_data, status_code = self.request_service.get_requests_by_staff(staff_id)
        return response_data, status_code

    def get_team_requests(self):
        staff_id = request.headers.get('X-Staff-ID')
        if not staff_id:
            return {"error": "Staff ID is required"}, 400

        response_data, status_code = self.request_service.get_team_requests(staff_id)
        return response_data, status_code

    def get_selected_request(self, request_id):
        response_data, status_code = self.request_service.get_selected_request(request_id)
        return response_data, status_code

    def approve_request(self, request_id):
        try:
            result_reason = request.json.get('result_reason')
            approved_dates = request.json.get('approved_dates')
            response_data, status_code = self.request_service.approve_request(request_id, result_reason, approved_dates)
            return response_data, status_code
        except Exception as e:
            # Log the exception if needed
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500

    def reject_request(self, request_id):
        try:
            result_reason = request.json.get('result_reason')
            response_data, status_code = self.request_service.reject_request(request_id, result_reason)
            return response_data, status_code
        except Exception as e:
            # Log the exception if needed
            current_app.logger.error("An error occurred: %s", str(e))
            return {"error": str(e)}, 500