from flask import jsonify, request

class RequestService:
    def __init__(self, supabase):
        self.supabase = supabase

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
                return {"error": "Failed to insert data into the database"}, 500

            # If everything is fine, return the inserted request
            return response.data[0], 201

        except Exception as e:
            return {"error": str(e)}, 500

    def get_requests_by_staff(self, staff_id: int):
        try:
            # Retrieve requests for the specified staff_id from the Supabase database
            response = self.supabase.from_("request").select("*").eq("staff_id", staff_id).execute()

            # Check for errors in the response
            if response is None:
                return {"error": "Failed to retrieve data from the database"}, 500

            # If no requests found, return a 404
            if not response.data:
                return {"error": "No requests found for this staff ID"}, 404

            # Return the retrieved requests
            return response.data, 200

        except Exception as e:
            return {"error": str(e)}, 500

class RequestController:
    def __init__(self, request_service):
        self.request_service = request_service

    def create_request(self):
        # Get form data from the request
        form_data = request.json
        
        # Call the service to create a request
        response_data, status_code = self.request_service.create_request(form_data)
        
        # Return the response
        return jsonify(response_data), status_code

    def get_requests_by_staff(self):
        # Get the staff_id from request arguments or headers
        staff_id = request.args.get('staff_id')
        
        # Validate staff_id
        if not staff_id:
            return jsonify({"error": "Staff ID is required"}), 400
        
        # Call the service to get requests by staff_id
        response_data, status_code = self.request_service.get_requests_by_staff(staff_id)
        
        # Return the response
        return jsonify(response_data), status_code
