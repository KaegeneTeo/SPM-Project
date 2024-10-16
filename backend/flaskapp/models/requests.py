class RequestService:
    def __init__(self, supabase):
        self.supabase = supabase

    def create_request(self, form_data):
        # Validate input
        if not form_data:
            return {"error": "No request data provided"}, 400
        try:
            # Insert new request into the Supabase database
            print(form_data)
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

            if response == None:
                return {"error": "Failed to insert data into the database"}, 500

            # If everything is fine, return the inserted request with a 201 status
            return response.data[0], 201
        except Exception as e:
            return {"error": str(e)}, 500
        
    def get_requests_by_staff(self, staff_id: int):
        try:
            # Retrieve requests for the specified staff_id from the Supabase database
            response = self.supabase.from_("request").select("*").eq("staff_id", staff_id).execute()
            print(response)
            # Check for errors in the response
            if response == None:
                return {"error": response["error"]["message"]}, 500
            
            # If no requests found, return a 404
            if response.data == []:
                return {"error": "No requests found for this staff ID"}, 404

            # Return the retrieved requests with a 200 status
            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500