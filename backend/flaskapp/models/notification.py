class notification_engine:
    #init
    def __init__(self, supabase):
        self.supabase = supabase
    
    #compose email on accepted schedule
    def compose_on_accept(self, request_id):
        email = ""
        request_response = self.supabase.from_("schedules").select("*").eq("request_id", request_id).execute()

        if not request_response.data:
            return {"error": "Schedules not found"}, 404

        selected_request = request_response.data
        schedulelist = list(selected_request)
        dict

        

