# employees_routes.py
from flask import Blueprint
from ..models.employees import EmployeesService, EmployeesController
from ..extensions import supabase

# Initialize Blueprint
employees_blueprint = Blueprint("employees", __name__)

# Initialize Service and Controller
employees_service = EmployeesService(supabase)
employees_controller = EmployeesController(employees_service)

# Define routes
@employees_blueprint.route("/employees", methods=['GET'])
def get_employees():
    return employees_controller.get_employees()

@employees_blueprint.route("/employees", methods=['PUT'])
def update_employee():
    return employees_controller.update_employee()

@employees_blueprint.route("/getstaffid", methods=['GET'])
def get_staff_id():
    return employees_controller.get_staff_id()
