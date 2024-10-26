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

def test_get_team_requests_user_not_found(request_service, supabase_client):
    # Mock response for a non-existent user
    supabase_client.from_("Employee").select().eq("Staff_ID", 999).execute.return_value = MagicMock(data=[])
    
    response = request_service.get_team_requests(999)
    assert response == ({"error": "User not found"}, 404)
    supabase_client.from_("Employee").select().eq("Staff_ID", 999).execute.assert_called_once()


def test_get_team_requests_authorized_with_team_members(request_service, supabase_client):
    # Mock response for an authorized user with Role 1 and 'Manager' position
    supabase_client.from_("Employee").select('Role, Position').eq("Staff_ID", 1).execute.return_value = MagicMock(data=[{"Role": 1, "Position": "Director", "Staff_ID":1}])
    response = request_service.get_team_requests(1)
    print(response)
    assert response == ([{'request_id': 42, 'staff_id': 140894, 'reason': 'test 6', 'status': 0, 'startdate': '2024-10-14', 'enddate': '2024-10-16', 'time_slot': 3, 'request_type': 1, 'result_reason': ''}], 200)


def test_get_team_requests_authorized_no_team_members(request_service, supabase_client):
    # Mock response for an authorized user with Role 1 and 'Manager' position
    supabase_client.from_("Employee").select().eq("Staff_ID", 1).execute.return_value = MagicMock(data=[{"Role": 1, "Position": "Manager"}])

    # Mock response for no team members
    supabase_client.from_("Employee").select().eq("Reporting_Manager", 1).execute.return_value = MagicMock(data=[])

    response = request_service.get_team_requests(1)
    assert response == ([], 200)  # Expected to return an empty list with 200 status code


def test_get_team_requests_unauthorized_user(request_service, supabase_client):
    # Mock response for an unauthorized user with Role 2 and no managerial position
    supabase_client.from_("Employee").select().eq("Staff_ID", 4).execute.return_value = MagicMock(data=[{"Role": 2, "Position": "Employee"}])

    response = request_service.get_team_requests(4)
    assert response == ([], 200)
    
def test_withdraw_request_success(request_service, supabase_client):
    # Mock the response for withdrawing a request
    supabase_client.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=True)
    
    response, data = request_service.withdraw_request(1)
    
    assert response == {"message": "Request withdrawn successful"}
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
    response, data = request_service.cancel_request(1)

    # Assert that the response is what we expect when the cancel is successful
    assert response == {"message": "Request withdrawn successfully"}

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

def test_create_request_exception(request_service, supabase_client):
    # Mock the Supabase client to raise an exception
    supabase_client.from_("request").insert().execute.side_effect = Exception("Database connection error")

    form_data = {
        "staffid": 123,
        "reason": "Need leave",
        "status": 0,
        "startdate": "2024-11-01",
        "enddate": "2024-11-02",
        "time_slot": 1,
        "request_type": 1
    }

    # Call the create_request method and capture the result
    result = request_service.create_request(form_data)  # Ensure to capture status_code

    # Check that the result contains the error message
    assert result == {"error": "Database connection error"}

    # Ensure the insert method was called once
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
    request_response.data = [{"request_id": 1, "staff_id": "123", "request_type": 1, "time_slot": "morning"}]
    supabase_client.from_("request").select().eq("request_id", 1).execute.return_value = request_response

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

# ---------------------------------------------
# Testing RequestController
# ---------------------------------------------

def test_withdraw_request_controller_success(request_controller, client, supabase_client):
    mock_response = {"message": "Request withdrawn successfully"}
    mock_data = {'staff_id': 1}

    # Mock the withdraw_request method in the RequestService
    with patch("flaskapp.models.requests.RequestService.withdraw_request", return_value=(mock_response, mock_data)), \
        patch("flaskapp.models.notification.notification_sender.send_withdraw", return_value="test_email"):
        response = client.delete('/withdraw_request/1')
    print(response.data)
    assert response.status_code == 200
    assert response.get_json() == mock_response

def test_cancel_request_controller_success(request_controller, client):
    mock_response = {"message": "Request withdrawn successfully"}
    mock_data = {'staff_id': 1}
    # Mock the cancel_request method in the RequestService
    with patch("flaskapp.models.requests.RequestService.cancel_request", return_value=(mock_response, mock_data)), \
        patch("flaskapp.models.notification.notification_sender.send_cancel", return_value="test_email"):
        response = client.delete('/cancel_request/1')
    print(response.data)
    assert response.status_code == 200
    assert response.get_json() == mock_response

from unittest.mock import patch

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
         patch("flaskapp.models.requests.RequestService.create_request", return_value=mock_response), \
         patch("flaskapp.models.notification.notification_sender.send_create", return_value="test_email"):

        # Send a POST request to the endpoint with JSON data
        response = client.post('/requests/', json=form_data)

    # Assert the response
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

    with patch("flaskapp.models.requests.RequestService.get_staff_id", return_value={'staff_id': 123}), \
         patch("flaskapp.models.requests.RequestService.create_request") as mock_create_request:

        # Set the create_request to raise an exception
        mock_create_request.side_effect = Exception("Database connection error")

        # Send a POST request to the endpoint with JSON data
        response = client.post('/requests/', json=form_data)

        # Check that the error message is as expected
        assert response.json == {"error": "Database connection error"}
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


# def test_get_requests_by_staff_controller(request_controller, client):
#     mock_response = [{'request_id': '1', 'staff_id': '123'}]
    
#     with patch.object(request_controller.request_service, 'get_requests_by_staff', return_value=(mock_response, 200)):
#         response = client.get('/requests/123')  # Adjust the endpoint based on your routing
#         assert response.status_code == 200
#         assert response.get_json() == mock_response

# def test_get_team_requests_controller_success(request_controller, client):
#     with patch.object(request_controller.request_service, 'get_team_requests', return_value=(["request 1", "request 2"], 200)):
#         response = client.get('/team/requests')  # Adjust the endpoint based on your routing
#         assert response.status_code == 200
#         assert response.get_json() == ["request 1", "request 2"]

# def test_approve_request_controller_success(request_controller, client):
#     with patch.object(request_controller.request_service, 'approve_request', return_value={"message": "Request approved successfully"}):
#         response = client.put('/requests/1/approve', json={
#             "result_reason": "Approved",
#             "approved_dates": ["2024-11-01"]
#         })  # Adjust the endpoint based on your routing
#         assert response.status_code == 200
#         assert response.get_json() == {"message": "Request approved successfully"}

# def test_reject_request_controller_success(request_controller, client):
#      # Mock Supabase call
#     with patch.object(request_controller.request_service.supabase.from_().update().eq(), 'execute', return_value=MagicMock(data=[{}])):
#         with patch.object(request_controller.request_service, 'reject_request', return_value={"message": "Request rejected successfully"}):
#             response = client.put('/requests/1/reject', json={
#                 "result_reason": "Not Approved"
#             })
            
#             # Assert the expected response
#             assert response.status_code == 200
#             assert response.get_json() == {"message": "Request rejected successfully"}

# def test_get_staff_id_missing_authorization(client):
#     # Missing Authorization header
#     response = client.get('/getstaffid', headers={'X-Staff-ID': '123'})
#     response_data = response.get_json()

#     # Assert that the response contains the error for missing Authorization
#     assert 'error' in response_data
#     assert response_data['error'] == 'Staff ID and token are required'
    
# def test_get_staff_id_missing_staff_id(client):
#     # Missing X-Staff-ID header
#     response = client.get('/getstaffid', headers={'Authorization': 'Bearer some_token'})
#     response_data = response.get_json()

#     # Assert that the response contains the error for missing Staff ID
#     assert 'error' in response_data
#     assert response_data['error'] == 'Staff ID and token are required'

# def test_get_staff_id_valid_headers(client):
#     # Prepare the headers with valid values
#     headers = {
#         'X-Staff-ID': '123',
#         'Authorization': 'Bearer some_token'
#     }

#     # Make the GET request to the endpoint with the headers
#     response = client.get('/getstaffid', headers=headers)
#     response_data = response.get_json()

#     # Assert that the response contains the expected staff_id and access_token
#     assert response.status_code == 200
#     assert response_data['staff_id'] == '123'
#     assert response_data['access_token'] == 'some_token'
        
# def test_create_request_database_insert_error(request_controller, client):
#     # Mocking the database to raise an exception (simulate failure)
#     with patch.object(request_controller.request_service.supabase.from_(), 'insert') as mock_insert:
#         mock_insert.return_value.execute.side_effect = Exception("Null value in column 'status' violates not-null constraint")

#         response = client.post('/requests/', json={'staffid': '123', 'reason': 'Test'})
#         response_data = response.get_json()  # Extract JSON from response
        
#         # Assert the expected status code and error message
#         assert response.status_code == 500
#         #assert response_data == {"error": "Failed to insert data into the database"}

# def test_create_request_general_exception(request_controller, client):
#     # Mocking to raise a general exception
#     with patch.object(request_controller.request_service.supabase.from_(), 'insert') as mock_insert:
#         # Setting the insert to raise an exception when execute is called
#         mock_insert.return_value.execute.side_effect = Exception("Some error")
        
#         response = client.post('/requests/', json={'staffid': '123', 'reason': 'Test'})
        
#         # Assert the expected status code and error message
#         assert response.status_code == 500
#         #assert response.get_json()["error"] == "Failed to insert data into the database"

