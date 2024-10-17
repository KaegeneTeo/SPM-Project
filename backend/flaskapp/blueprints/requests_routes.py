from flask import Blueprint
from ..extensions import supabase  # Assuming you have initialized supabase
from ..models.requests import RequestService, RequestController

requests_blueprint = Blueprint("requests", __name__)

# Initialize services and controllers
request_service = RequestService(supabase)
request_controller = RequestController(request_service)

# Define routes
@requests_blueprint.route('/requests', methods=['POST'])
def create_request():
    return request_controller.create_request()

@requests_blueprint.route('/requests', methods=['GET'])
def get_requests_by_staff():
    return request_controller.get_requests_by_staff()

