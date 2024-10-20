# teams_routes.py
from flask import Blueprint
from ..models.teams import TeamsService, TeamsController
from flask_supabase import Supabase
from ..extensions import supabase

# Initialize Blueprint
teams_blueprint = Blueprint("teams", __name__)

# Initialize Service and Controller
teams_service = TeamsService(supabase)
teams_controller = TeamsController(teams_service)

# Define routes
@teams_blueprint.route("/teams_by_reporting_manager", methods=['GET'])
def get_teams_by_reporting_manager():
    return teams_controller.get_teams_by_reporting_manager()

@teams_blueprint.route('/team_details', methods=['GET'])
def get_team_details():
    return teams_controller.get_team_details()
