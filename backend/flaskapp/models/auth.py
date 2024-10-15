# auth_service.py
class AuthService:
    def __init__(self, supabase):
        self.supabase = supabase

    def login(self, email, password):
        try:
            # Sign in using Supabase Auth
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # Prepare the response with email and tokens
            json_response = {
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }

            # Fetch staff_id, role, dept, reporting_manager from Employee table
            staff_response = self.supabase.from_("Employee").select("Staff_ID, Role, Dept, Reporting_Manager").ilike("Email", json_response["email"]).execute()

            if staff_response.data:
                json_response["staff_id"] = staff_response.data[0]["Staff_ID"]
                json_response["role"] = staff_response.data[0]["Role"]
                json_response["dept"] = staff_response.data[0]["Dept"]
                json_response["reporting_manager"] = staff_response.data[0]["Reporting_Manager"]
            else:
                json_response["staff_id"] = None
                json_response["role"] = None
                json_response["dept"] = None
                json_response["reporting_manager"] = None

            return json_response, 200

        except Exception as e:
            return {"message": str(e)}, 400

    def logout(self):
        try:
            # Sign out using Supabase Auth
            self.supabase.auth.sign_out()
            return {"message": "User signed out successfully."}, 200
        except Exception as e:
            return {"message": str(e)}, 400

    def check_auth(self, access_token):
        try:
            # Validate the token
            response = self.supabase.auth.get_user(access_token)

            if response is not None:
                json = {
                    "email": response.user.email,
                    "role": response.user.role,
                    "access_token": access_token,
                    "refresh_token": response.session.refresh_token,
                }
                return json, 200
            else:
                return {}, 404

        except Exception as e:
            return {"message": str(e)}, 400
