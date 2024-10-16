from flask import Blueprint, jsonify, request
from ..extensions import supabase  # Assuming supabase is initialized here
from ..models.schedules import SchedulesService

# schedules_controller.py
schedules_blueprint = Blueprint("schedules", __name__)

# Initialize the service with the Supabase client
schedules_service = SchedulesService(supabase)

@schedules_blueprint.route("/")
def test():
    return jsonify("Hello world"), 200

@schedules_blueprint.route("/schedules", methods=['GET'])
def get_schedules():
    data = request.args
    print(data)

    CEO = schedules_service.get_ceo()

    # Special case for CEO department
    if data["dept"] == "CEO":
        allnames = schedules_service.get_all_employees_by_dept(data["dept"])
        response = schedules_service.get_schedules_by_dept(data["dept"])

    # Filter for all departments
    elif data["dept"] == "all" and data["reporting_manager"] == "all":
        allnames = schedules_service.get_all_employees()
        response = schedules_service.get_schedules_for_all_depts()

    # Filter for all teams in a department
    elif data["reporting_manager"] == "all" and data["dept"] != "all":
        allnames = schedules_service.get_all_employees_by_dept(data["dept"])
        response = schedules_service.get_schedules_by_dept(data["dept"])

    # Director team (special logic)
    elif int(data["role"]) == 1 and int(data["reporting_manager"]) == CEO:
        allnames = schedules_service.get_all_directors(data["reporting_manager"])
        response = schedules_service.get_directors_schedules(data["dept"], data["reporting_manager"])

    # Filter by department and reporting manager
    else:
        allnames = schedules_service.get_all_employees_by_reporting_manager(data["dept"], int(data["reporting_manager"]))
        response = schedules_service.get_schedules_by_reporting_manager(data["dept"], int(data["reporting_manager"]))

    # Format and return the schedule data
    return jsonify(schedules_service.format_schedules(response, allnames))
