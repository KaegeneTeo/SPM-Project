from flask import Blueprint
from ..extensions import supabase  # Assuming you have initialized supabase
from ..models.requests import RequestService, RequestController

requests_blueprint = Blueprint("requests", __name__)

# Initialize services and controllers
request_service = RequestService(supabase)
request_controller = RequestController(request_service)

# Define routes
@requests_blueprint.route("/getstaffid", methods=['GET'])
def get_staff_id():
    return request_controller.get_staff_id()

@requests_blueprint.route("/requests/", methods=['POST'])
def create_request():
    return request_controller.create_request()

@requests_blueprint.route("/requests/<int:staff_id>", methods=['GET'])
def get_requests_by_staff(staff_id: int):
    return request_controller.get_requests_by_staff(staff_id)

@requests_blueprint.route('/team/requests', methods=['GET'])
def get_team_requests():
    return request_controller.get_team_requests()

@requests_blueprint.route("/request/<request_id>", methods=['GET'])
def get_selected_request(request_id):
    return request_controller.get_selected_request(request_id)

@requests_blueprint.route("/request/<request_id>/approve", methods=['PUT', 'POST'])
def request_approve(request_id):
    return request_controller.approve_request(request_id)

@requests_blueprint.route("/request/<request_id>/reject", methods=['PUT'])
def request_reject(request_id):
    return request_controller.reject_request(request_id)