from flask import jsonify, request, current_app


class EmployeesService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_all_employees(self):
        with current_app.app_context():
            response = self.supabase.from_('Employee').select("*").execute()
            return response.data

    def update_employee(self, employee_id, form_data):
        with current_app.app_context():
            response = self.supabase.from_('Employee').update(form_data).eq('Staff_ID', employee_id).execute()
            return response

    def get_staff_id_from_headers(self, staff_id):
        # Fetch the employee details from the database based on staff ID
        with current_app.app_context():
            response = self.supabase.from_('Employee').select('*').eq('Staff_ID', staff_id).execute()
            return response.data

class EmployeesController:
    def __init__(self, employees_service):
        self.employees_service = employees_service

    def check_online(self):
        return "Hello employees", 200

    def get_employees(self):
        employees = self.employees_service.get_all_employees()
        return jsonify(employees), 200

    def update_employee(self):
        form_data = request.form
        staff_id = request.headers.get('X-Staff-ID')  # Assuming staff_id is passed in headers
        if not staff_id:
            return jsonify({"error": "Staff ID is required"}), 400
        update_response = self.employees_service.update_employee(staff_id, form_data)
        if update_response.status_code == 200:
            return jsonify({"message": "Employee updated successfully"}), 200
        return jsonify({"error": "Failed to update employee"}), 500

    def get_staff_id(self):
        staff_id = request.headers.get('X-Staff-ID')
        access_token = request.headers.get('Authorization').split(' ')[1]  # Extract Bearer token
        if not staff_id or not access_token:
            return jsonify({"error": "Staff ID and token are required"}), 400
        
        staff_details = self.employees_service.get_staff_id_from_headers(staff_id)
        return jsonify({
            "message": "CORS is working", 
            "staff_id": staff_id, 
            "access_token": access_token,
            "staff_details": staff_details
        }), 200
