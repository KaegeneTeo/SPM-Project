import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify, request, abort, current_app
from flaskapp.models.requests import RequestService, RequestController
from flaskapp.blueprints.requests_routes import requests_blueprint
from datetime import datetime, timedelta
from werkzeug.exceptions import NotFound


@pytest.fixture
def supabase_client():
    return MagicMock()

@pytest.fixture
def mock_staff_id():
    return 123  # Example staff_id

@pytest.fixture
def request_service(supabase_client):
    return RequestService(supabase_client)

@pytest.fixture
def request_controller(request_service):
    return RequestController(request_service)

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(requests_blueprint)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ---------------------------------------------
# Testing RequestService
# ---------------------------------------------
def test_single_time_slot_insert(request_service, supabase_client):
    # Mocking insert response for single time slot

    # Call the method with a time slot other than 3
    request_service.create_schedule_entries(staff_id=123, dates=["2024-10-26"], time_slot=1, request_id=456)

    # Assert that one insert call was made with the correct parameters
    supabase_client.from_("schedule").insert.assert_called_once_with({
        "staff_id": 123,
        "date": "2024-10-26",
        "time_slot": 1,
        "request_id": 456
    })

def test_multiple_time_slots_insert(request_service, supabase_client):
    # Mock insert responses for time slot 3 scenario
    mock_response1 = MagicMock()
    mock_response2 = MagicMock()
    supabase_client.from_().insert().execute.side_effect = [mock_response1, mock_response2]

    # Call the method with time slot 3
    request_service.create_schedule_entries(staff_id=123, dates=["2024-10-26"], time_slot=3, request_id=456)

    # Assert that two insert calls were made with time slots 1 and 2
    expected_calls = [
        {"staff_id": 123, "date": "2024-10-26", "time_slot": 1, "request_id": 456},
        {"staff_id": 123, "date": "2024-10-26", "time_slot": 2, "request_id": 456}
    ]
    supabase_client.from_("schedule").insert.assert_any_call(expected_calls[0])
    supabase_client.from_("schedule").insert.assert_any_call(expected_calls[1])

def test_invalid_time_slot_type(request_service, supabase_client):
    # Mocking insert response

    # Call the method with a non-integer, non-numeric string time slot (should skip insertion)
    request_service.create_schedule_entries(123, ["2024-10-26"], "invalid", 456)

    # Assert no insertion was attempted due to invalid time slot
    supabase_client.from_("schedule").insert.assert_not_called()

def test_user_not_found(request_service, mock_staff_id):
    # Mock supabase response for non-existent user
    request_service.supabase.from_().select().eq().execute.return_value.data = None

    result, status_code = request_service.get_team_requests(mock_staff_id)

    assert result == {"error": "User not found"}
    assert status_code == 404

def test_user_not_authorized(request_service, mock_staff_id):
    # Mock user response with unauthorized role and position
    request_service.supabase.from_().select().eq().execute.return_value.data = [
        {"Role": 2, "Position": "employee"}
    ]

    result, status_code = request_service.get_team_requests(mock_staff_id)

    assert result == []
    assert status_code == 401

def test_manager_with_no_team_members(request_service, mock_staff_id):
    # Mock authorized role and position
    request_service.supabase.from_().select().eq().execute.side_effect = [
        MagicMock(data=[{"Role": 1, "Position": "manager"}]),  # User role lookup
        MagicMock(data=[])  # No team members found
    ]

    result, status_code = request_service.get_team_requests(mock_staff_id)

    assert result == []
    assert status_code == 404

def test_manager_with_team_members_and_requests(request_service, mock_staff_id):
    # Mock authorized role and position, team members, and requests
    request_service.supabase.from_().select().eq().execute.side_effect = [
        MagicMock(data=[{"Role": 1, "Position": "manager"}]),  # User role lookup
        MagicMock(data=[{"Staff_ID": 124}, {"Staff_ID": 125}]),  # Team members
        MagicMock(data=[{"staff_id": 124, "request": "Request 1"}])
    ]

    request_service.supabase.from_().select().in_().eq().execute.return_value = MagicMock(data=[{"staff_id": 125, "request": "Request 2"}])

    result, status_code = request_service.get_team_requests(mock_staff_id)

    expected_result = [
        {"staff_id": 125, "request": "Request 2"}
    ]
    print(result)
    assert result == expected_result
    assert status_code == 200


def test_manager_with_team_members_but_no_requests(request_service, mock_staff_id):
    # Mock authorized role and position, team members, and empty requests
    request_service.supabase.from_().select().eq().execute.side_effect = [
        MagicMock(data=[{"Role": 1, "Position": "manager"}]),  # User role lookup
        MagicMock(data=[{"Staff_ID": 124}, {"Staff_ID": 125}])  # No requests for team members
    ]

    request_service.supabase.from_().select().in_().eq().execute.return_value = MagicMock(data=[])

    result, status_code = request_service.get_team_requests(mock_staff_id)

    assert result == []
    assert status_code == 200

def test_get_selected_request_success(request_service, supabase_client):
    # Mock the response for getting a request
    supabase_client.from_("request").select().eq("request_id", 1).execute.return_value = MagicMock(data=[{"request_id": 1}])

    response = request_service.get_selected_request(1)
    assert response == ({"request_id": 1}, 200)  # Expecting a tuple
    supabase_client.from_("request").select().eq("request_id", 1).execute.assert_called_once()

def test_get_selected_request_not_found(request_service, supabase_client):
    # Mock the response to simulate a request not found scenario
    supabase_client.from_("request").select().eq("request_id", 999).execute.return_value = MagicMock(data=[])

    response = request_service.get_selected_request(999)
    assert response == ({"error": "Request not found"}, 404)  # Expecting an error message and 404 status
    supabase_client.from_("request").select().eq("request_id", 999).execute.assert_called_once()

def test_calculate_recurring_dates_empty_input(request_service):
    # Test with empty approved_dates input
    result = request_service.calculate_recurring_dates([])
    assert result == []  # Expecting an empty list when there are no approved dates


def test_calculate_recurring_dates_single_date(request_service):
    # Test with a single approved date
    approved_dates = ["2024-01-01"]  # A Monday
    result = request_service.calculate_recurring_dates(approved_dates)
    
    # Generate expected dates for all Mondays within one year from 2024-01-01
    expected_dates = []
    start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end_date = start_date + timedelta(days=365)
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == 0:  # Monday
            expected_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    assert result == expected_dates  # Verify the generated list of dates matches expected Mondays


def test_calculate_recurring_dates_multiple_dates(request_service):
    # Test with multiple approved dates (Monday and Wednesday)
    approved_dates = ["2024-01-01", "2024-01-03"]  # Monday and Wednesday
    result = request_service.calculate_recurring_dates(approved_dates)

    # Generate expected dates for all Mondays and Wednesdays within one year from 2024-01-01
    expected_dates = []
    start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end_date = start_date + timedelta(days=365)
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() in [0, 2]:  # Monday or Wednesday
            expected_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    assert result == expected_dates  # Verify the generated list of dates matches expected Mondays and Wednesdays

def test_withdraw_request_success(request_service, supabase_client):
    # Mock the response for withdrawing a request
    supabase_client.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=True)
    
    response, status_code = request_service.withdraw_request(1)
    
    assert status_code == 200
    assert response["message"] == "Request withdrawn successful"
    supabase_client.from_("request").delete().eq("request_id", 1).execute.assert_called_once()

def test_withdraw_request_not_found(request_service, supabase_client):
    # Mock the response to simulate that no request was found
    supabase_client.from_("request").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    # Call the withdraw_request method
    response = request_service.withdraw_request(999)

    # Assert that the response is what we expect when the request is not found
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_client.from_("request").delete().eq("request_id", 999).execute.assert_called_once()

def test_cancel_request_success(request_service, supabase_client):
    # Mock the responses to simulate a successful cancel
    supabase_client.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=[{"request_id": 1}])
    supabase_client.from_("schedule").delete().eq("request_id", 1).execute.return_value = MagicMock(data=[{"request_id": 1}])

    # Call the cancel_request method
    response, status_code = request_service.cancel_request(1)

    # Assert that the response is what we expect when the cancel is successful
    assert response["message"] == "Request cancel successful"
    assert status_code == 200

def test_cancel_request_not_found(request_service, supabase_client):
    # Mock the responses to simulate a request not found
    supabase_client.from_("request").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)
    supabase_client.from_("schedule").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    # Call the cancel_request method
    response = request_service.cancel_request(999)

    # Assert that the response is what we expect when the request is not found
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)

def test_create_request_success(request_service, supabase_client):
    supabase_response = MagicMock()
    supabase_response.data = [{"request_id": 1, "staff_id": "123"}]
    supabase_client.from_("request").insert().execute.return_value = supabase_response

    form_data = {
        "staffid": 123,
        "reason": "Need leave",
        "status": 0,
        "startdate": "2024-11-01",
        "enddate": "2024-11-02",
        "time_slot": 1,
        "request_type": 1
    }

    result, status_code = request_service.create_request(form_data)
    assert status_code == 201
    assert result == {"request_id": 1, "staff_id": "123"}
    supabase_client.from_("request").insert().execute.assert_called_once()

def test_create_request_insert_failure(request_service, supabase_client, client):
    # Use the application context for current_app.logger
    with client.application.app_context():
        # Mock the Supabase client to return None for execute to simulate a failure
        supabase_client.from_("request").insert().execute.return_value = None

        form_data = {
            "staffid": 123,
            "reason": "Need leave",
            "status": 0,
            "startdate": "2024-11-01",
            "enddate": "2024-11-02",
            "time_slot": 1,
            "request_type": 2
        }

        result, status_code = request_service.create_request(form_data)
        assert status_code == 500
        assert result == {"error": "Failed to insert data into the database"}
        supabase_client.from_("request").insert().execute.assert_called_once()


def test_create_request_exception_handling(request_service, supabase_client, client):
    # Use the application context for current_app.logger
    with client.application.app_context():
        # Mock the Supabase client to raise an exception
        supabase_client.from_("request").insert().execute.side_effect = Exception("Database connection error")

        form_data = {
            "staffid": 123,
            "reason": "Need leave",
            "status": 0,
            "startdate": "2024-11-01",
            "enddate": "2024-11-02",
            "time_slot": 1,
            "request_type": 2
        }

        result, status_code = request_service.create_request(form_data)

        # Assert that the error was handled correctly
        assert status_code == 500
        assert result == {"error": "Database connection error"}
        supabase_client.from_("request").insert().execute.assert_called_once()

def test_create_request_invalid_input(request_service):
    result, status_code = request_service.create_request(None)
    assert status_code == 400
    assert result == {"error": "No request data provided"}

def test_get_requests_by_staff_success(request_service, supabase_client):
    supabase_response = MagicMock()
    supabase_response.data = [{"request_id": 1, "staff_id": "123"}]
    supabase_client.from_("request").select().eq("staff_id", "123").execute.return_value = supabase_response

    result, status_code = request_service.get_requests_by_staff("123")
    assert status_code == 200
    assert result == [{"request_id": 1, "staff_id": "123"}]
    supabase_client.from_("request").select().eq("staff_id", "123").execute.assert_called_once()

def test_get_requests_by_staff_not_found(request_service, supabase_client):
    supabase_response = MagicMock()
    supabase_response.data = []
    supabase_client.from_("request").select().eq("staff_id", "123").execute.return_value = supabase_response

    result, status_code = request_service.get_requests_by_staff("123")
    assert status_code == 404
    assert result == {"error": "No requests found for this staff ID"}
    supabase_client.from_("request").select().eq("staff_id", "123").execute.assert_called_once()

def test_approve_request_success(request_service, supabase_client):
    request_response = MagicMock()
    request_response.data = [{"request_id": 1, "staff_id": "123", "request_type": 1, "time_slot": 2}]
    supabase_client.from_("request").select().eq("request_id", 1).execute.return_value = request_response

    request_service.create_schedule_entries = MagicMock()

    result = request_service.approve_request(1, "Approved", ["2024-11-01"])
    assert result == ({"message": "Request approved successfully"}, 200)
    supabase_client.from_("request").select().eq("request_id", 1).execute.assert_called_once()

def test_approve_request_success_recurring(request_service, supabase_client):
    request_response = MagicMock()
    request_response.data = [{"request_id": 1, "staff_id": "123", "request_type": 2, "time_slot": 2}]
    supabase_client.from_("request").select().eq("request_id", 1).execute.return_value = request_response

    request_service.calculate_recurring_dates = MagicMock()
    request_service.create_schedule_entries = MagicMock()

    result = request_service.approve_request(1, "Approved", ["2024-11-01"])
    assert result == ({"message": "Request approved successfully"}, 200)
    supabase_client.from_("request").select().eq("request_id", 1).execute.assert_called_once()

def test_approve_request_not_found(request_service, supabase_client):
    supabase_client.from_("request").select().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    response = request_service.approve_request(999, "Approved", ["2023-01-01"])
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_client.from_("request").select().eq("request_id", 999).execute.assert_called_once()

def test_reject_request_success(request_service, supabase_client):
    supabase_response = MagicMock()
    supabase_response.data = True
    supabase_client.from_("request").update().eq("request_id", 1).execute.return_value = supabase_response

    result = request_service.reject_request(1, "Not Approved")
    assert result == ({"message": "Request rejected successfully"}, 200)
    supabase_client.from_("request").update().eq("request_id", 1).execute.assert_called_once()

def test_reject_request_not_found(request_service, supabase_client):
    supabase_client.from_("request").update().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    response = request_service.reject_request(999, "Rejected")
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_client.from_("request").update().eq("request_id", 999).execute.assert_called_once()

def test_create_schedule_entries_response1_none(request_service, supabase_client, client, caplog):
    # Use the application context for current_app.logger
    with client.application.app_context(), caplog.at_level("ERROR"):
        # Set up mock for supabase execute to return None for response1
        supabase_client.from_("schedule").insert().execute.side_effect = [None, MagicMock()]

        staff_id = 123
        dates = ["2024-11-01"]
        time_slot = 3
        request_id = 456

        # Call the function
        request_service.create_schedule_entries(staff_id, dates, time_slot, request_id)

        # Check the log for the correct error message
        assert any("Failed to create schedule entry for date 2024-11-01 with time_slot 1" in record.message for record in caplog.records)

        # Verify the execute call was made
        supabase_client.from_("schedule").insert().execute.assert_called()

def test_create_schedule_entries_response2_none(request_service, supabase_client, client):
    # Use the application context for current_app.logger
    with client.application.app_context():
        # Mock the Supabase client so that the second insert returns None
        supabase_client.from_("schedule").insert().execute.side_effect = [MagicMock(), None]

        staff_id = 123
        dates = ["2024-11-01"]
        time_slot = 3
        request_id = 456

        # Call the create_schedule_entries method
        request_service.create_schedule_entries(staff_id, dates, time_slot, request_id)

        # Verify that the insert method was called twice
        assert supabase_client.from_("schedule").insert().execute.call_count == 2

def test_get_requests_by_staff_no_response(request_service, supabase_client, client):
    # Use the application context for current_app.logger
    with client.application.app_context():
        # Mock the Supabase client to return None for execute to simulate a database error
        supabase_client.from_("request").select().eq().execute.return_value = None

        staff_id = 123

        result, status_code = request_service.get_requests_by_staff(staff_id)

        # Assert that the error was handled correctly
        assert status_code == 500
        assert result == {"error": "Failed to retrieve data from the database"}
        supabase_client.from_("request").select().eq().execute.assert_called_once()

def test_get_requests_by_staff_exception_handling(request_service, supabase_client, client):
    # Use the application context for current_app.logger
    with client.application.app_context():
        # Mock the Supabase client to raise an exception
        supabase_client.from_("request").select().eq().execute.side_effect = Exception("Unexpected error")

        staff_id = 123

        result, status_code = request_service.get_requests_by_staff(staff_id)

        # Assert that the error was handled correctly
        assert status_code == 500
        assert result == {"error": "Unexpected error"}
        supabase_client.from_("request").select().eq().execute.assert_called_once()

# ---------------------------------------------
# Testing RequestController
# ---------------------------------------------

def test_withdraw_request_controller_success(request_controller, client, supabase_client):
    mock_response = {"message": "Request withdrawn successful", "data": {"request_id": 1}}
    mock_data = {'staff_id': 1}

    # Mock the withdraw_request method in the RequestService
    with patch("flaskapp.models.requests.RequestService.withdraw_request", return_value=(mock_response, mock_data)), \
        patch("flaskapp.models.notification.notification_sender.send_withdraw", return_value="test_email"):
        response = client.delete('/withdraw_request/1')
    
    assert response.status_code == 200
    assert response.get_json() == mock_response

def test_withdraw_request_controller_exception(request_controller, client):
    # Mock the supabase `from_` call to raise an exception
    with patch("flaskapp.models.requests.RequestService.withdraw_request") as mock_withdraw_request:
        
        # Set the withdraw_request to raise an exception
        mock_withdraw_request.side_effect = Exception("Database connection error")
        # Send the delete request
        response = client.delete('/withdraw_request/1')
        
    # Verify the response
    assert response.status_code == 500
    assert response.get_json() == {"error": "Database connection error"}

def test_cancel_request_controller_success(request_controller, client):
    mock_response = {"message": "Request cancel successful", "data": {"request_id": 1}}
    mock_data = {'staff_id': 1}
    # Mock the cancel_request method in the RequestService
    with patch("flaskapp.models.requests.RequestService.cancel_request", return_value=(mock_response, mock_data)), \
        patch("flaskapp.models.notification.notification_sender.send_cancel", return_value="test_email"):
        response = client.delete('/cancel_request/1')
    
    assert response.status_code == 200
    assert response.get_json() == mock_response

def test_cancel_request_controller_exception(request_controller, client):
    # Mock the supabase `from_` call to raise an exception
    with patch("flaskapp.models.requests.RequestService.cancel_request") as mock_cancel_request:
        
        # Set the cancel_request to raise an exception
        mock_cancel_request.side_effect = Exception("Database connection error")
        # Send the delete request
        response = client.delete('/cancel_request/1')
        
    # Verify the response
    assert response.status_code == 500
    assert response.get_json() == {"error": "Database connection error"}

def test_create_request_controller_success(request_controller, client):
    form_data = {
        'staffid': 123,
        'reason': 'Test Reason',
        'status': 0,
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 1,
        'request_type': 2
    }

    # Mock the necessary methods
    mock_response = {'request_id': '1', 'staff_id': 123}

    with patch("flaskapp.models.requests.RequestService.get_staff_id", return_value={'staff_id': 123}), \
         patch("flaskapp.models.requests.RequestService.create_request", return_value=(mock_response, 201)), \
         patch("flaskapp.models.notification.notification_sender.send_create", return_value="test_email"):

        # Send a POST request to the endpoint with JSON data
        response = client.post('/requests/', json=form_data)

        # Assert the response
        assert response.status_code == 201
        assert response.get_json() == mock_response

def test_create_request_exception(request_controller, client):
    form_data = {
        'staffid': 123,
        'reason': 'Test Reason',
        'status': 0,
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 1,
        'request_type': 2
    }

    with patch("flaskapp.models.requests.RequestService.create_request") as mock_create_request:

        # Set the create_request to raise an exception
        mock_create_request.side_effect = Exception("Database connection error")

        # Send a POST request to the endpoint with JSON data
        response = client.post('/requests/', json=form_data)

        # Check that the error message is as expected
        assert response.json == {"error": "Database connection error"}
        assert response.status_code == 500

def test_get_team_requests_controller_success(request_controller, client):
    mock_response = {
        'request_id': 1, 
        'staff_id': 123,         
        'reason': 'Test Reason',
        'status': 0,
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 1,
        'request_type': 2
    }
    with patch("flaskapp.models.requests.RequestService.get_team_requests", return_value=(mock_response, 200)):
        response = client.get('/team/requests', headers={'X-Staff-ID': '123'})
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_get_team_requests_controller_missing_staff_id(request_controller, client):
    response = client.get('/team/requests')
    assert response.status_code == 400
    assert response.get_json() == {"error": "Staff ID is required"}

def test_get_selected_request_controller_success(request_controller, client):
    # Define a mock response to simulate a successful request retrieval
    mock_response = {
        'request_id': 1,
        'staff_id': 123,
        'reason': 'Test Reason',
        'status': 0,
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 1,
        'request_type': 2
    }

    # Mock the get_selected_request method in RequestService to return the mock response with status code 200
    with patch("flaskapp.models.requests.RequestService.get_selected_request", return_value=(mock_response, 200)):
        response = client.get('/request/1')  # Ensure this matches the route defined
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_get_requests_by_staff_controller_success(request_controller, client):
    # Define a mock response to simulate a successful request retrieval
    mock_response = {
        'request_id': 1,
        'staff_id': 123,
        'reason': 'Test Reason',
        'status': 0,
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 1,
        'request_type': 2
    }

    # Mock the get_selected_request method in RequestService to return the mock response with status code 200
    with patch("flaskapp.models.requests.RequestService.get_requests_by_staff", return_value=(mock_response, 200)):
        response = client.get('/requests/123')  
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_approve_request_controller_success(request_controller, client):
    # Define mock response to simulate a successful request approval
    mock_response = {"message": "Request approved successfully"}
    
    # Mock the approve_request method in RequestService
    with patch("flaskapp.models.requests.RequestService.approve_request", return_value=(mock_response, 200)), \
         patch("flaskapp.models.notification.notification_sender.send_approve", return_value="test_email"):
        
        # Make a PUT request to the approve endpoint with required JSON data
        response = client.put(
            '/request/1/approve',
            json={
                "result_reason": "Approved",
                "approved_dates": ["2024-11-01"]
            }
        )
        
        # Assert the response status code and response data
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_approve_request_controller_exception(request_controller, client):
    # Mock the supabase `from_` call to raise an exception
    with patch("flaskapp.models.requests.RequestService.approve_request") as mock_approve_request:
        
        # Set the cancel_request to raise an exception
        mock_approve_request.side_effect = Exception("Database connection error")
        # Send the delete request
        response = client.put(
            '/request/1/approve',
            json={
                "result_reason": "Approved",
                "approved_dates": ["2024-11-01"]
            }
        )
        
    # Verify the response
    assert response.status_code == 500
    assert response.get_json() == {"error": "Database connection error"}

def test_reject_request_controller_success(request_controller, client):
    # Define mock response to simulate a successful request approval
    mock_response = {"message": "Request rejected successfully"}
    
    # Mock the approve_request method in RequestService
    with patch("flaskapp.models.requests.RequestService.reject_request", return_value=(mock_response, 200)), \
         patch("flaskapp.models.notification.notification_sender.send_reject", return_value="test_email"):
        
        # Make a PUT request to the approve endpoint with required JSON data
        response = client.put(
            '/request/1/reject',
            json={
                "status": -1,
                "result_reason": "Rejected"
            }
        )
        
        # Assert the response status code and response data
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_reject_request_controller_exception(request_controller, client):
    # Mock the supabase `from_` call to raise an exception
    with patch("flaskapp.models.requests.RequestService.reject_request") as mock_reject_request:
        
        # Set the cancel_request to raise an exception
        mock_reject_request.side_effect = Exception("Database connection error")
        # Send the delete request
        response = client.put(
            '/request/1/reject',
            json={
                "status": -1,
                "result_reason": "Rejected"
            }
        )
        
    # Verify the response
    assert response.status_code == 500
    assert response.get_json() == {"error": "Database connection error"}

# ---------------------------------------------
# Testing Get Staff ID with different scenarios
# ---------------------------------------------
def test_get_staff_id_missing_authorization(client):
    # Missing Authorization header
    response = client.get('/getstaffid', headers={'X-Staff-ID': '123'})
    response_data = response.get_json()

    # Assert that the response contains the error for missing Authorization
    assert response_data['staff_id'] == '123'
    assert response_data['access_token'] == None

def test_get_staff_id_missing_staff_id(client):
    # Missing X-Staff-ID header
    response = client.get('/getstaffid', headers={'Authorization': 'Bearer some_token'})
    response_data = response.get_json()

    # Assert that the response contains the error for missing Staff ID
    assert response_data['staff_id'] == None
    assert response_data['access_token'] == 'some_token'

def test_get_staff_id_valid_headers(client):
    # Prepare the headers with valid values
    headers = {
        'X-Staff-ID': '123',
        'Authorization': 'Bearer some_token'
    }

    # Make the GET request to the endpoint with the headers
    response = client.get('/getstaffid', headers=headers)
    response_data = response.get_json()

    # Assert that the response contains the expected staff_id and access_token
    assert response.status_code == 200
    assert response_data['staff_id'] == '123'
    assert response_data['access_token'] == 'some_token'

""" 


def test_approve_request_controller_success(request_controller, client):
    with patch.object(request_controller.request_service, 'approve_request', return_value={"message": "Request approved successfully"}):
        response = client.put('/requests/1/approve', json={
            "result_reason": "Approved",
            "approved_dates": ["2024-11-01"]
        })  # Adjust the endpoint based on your routing
        assert response.status_code == 200
        assert response.get_json() == {"message": "Request approved successfully"}

def test_reject_request_controller_success(request_controller, client):
     # Mock Supabase call
    with patch.object(request_controller.request_service.supabase.from_().update().eq(), 'execute', return_value=MagicMock(data=[{}])):
        with patch.object(request_controller.request_service, 'reject_request', return_value={"message": "Request rejected successfully"}):
            response = client.put('/requests/1/reject', json={
                "result_reason": "Not Approved"
            })
            # Assert the expected response
            assert response.status_code == 400
            assert response.get_json() == {"message": "Request rejected successfully"}
" """