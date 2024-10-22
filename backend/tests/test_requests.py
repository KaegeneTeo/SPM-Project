import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify, request, abort, current_app
from flaskapp.models.requests import RequestService, RequestController
from datetime import datetime, timedelta
from werkzeug.exceptions import NotFound

# Flask app for testing the controller
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
    })
    return app

# Fixtures for mock objects
@pytest.fixture
def supabase_mock():
    return MagicMock()

@pytest.fixture
def request_service(supabase_mock):
    return RequestService(supabase_mock)

@pytest.fixture
def request_controller(request_service):
    return RequestController(request_service)

# ---------------------------------------------
# Testing RequestService
# ---------------------------------------------

def test_withdraw_request_success(request_service, supabase_mock):
    # Mock the response for withdrawing a request
    supabase_mock.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=True)
    
    response_data, status_code = request_service.withdraw_request(1)
    
    assert status_code == 200
    assert response_data == {"message": "Request withdrawn successfully"}
    supabase_mock.from_("request").delete().eq("request_id", 1).execute.assert_called_once()

def test_withdraw_request_not_found(request_service, supabase_mock):
    # Mock the response to simulate that no request was found
    supabase_mock.from_("request").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    # Call the withdraw_request method
    response = request_service.withdraw_request(999)

    # Assert that the response is what we expect when the request is not found
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_mock.from_("request").delete().eq("request_id", 999).execute.assert_called_once()

def test_cancel_request_success(request_service, supabase_mock):
    # Mock the responses to simulate a successful cancel
    supabase_mock.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=[{"request_id": 1}])
    supabase_mock.from_("schedule").delete().eq("request_id", 1).execute.return_value = MagicMock(data=[{"request_id": 1}])

    # Call the cancel_request method
    response, status_code = request_service.cancel_request(1)

    # Assert that the response is what we expect when the cancel is successful
    assert status_code == 200
    assert response == {"message": "Request withdrawn successfully"}

def test_cancel_request_not_found(request_service, supabase_mock):
    # Mock the responses to simulate a request not found
    supabase_mock.from_("request").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)
    supabase_mock.from_("schedule").delete().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    # Call the cancel_request method
    response = request_service.cancel_request(999)

    # Assert that the response is what we expect when the request is not found
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)

def test_create_request_success(request_service, supabase_mock):
    supabase_response = MagicMock()
    supabase_response.data = [{"request_id": 1, "staff_id": "123"}]
    supabase_mock.from_("request").insert().execute.return_value = supabase_response

    form_data = {
        "staffid": "123",
        "reason": "Need leave",
        "status": 0,
        "startdate": "2024-11-01",
        "enddate": "2024-11-02",
        "time_slot": "morning",
        "request_type": 1
    }

    result, status_code = request_service.create_request(form_data)
    assert status_code == 201
    assert result == {"request_id": 1, "staff_id": "123"}
    supabase_mock.from_("request").insert().execute.assert_called_once()

def test_create_request_invalid_input(request_service):
    result, status_code = request_service.create_request(None)
    assert status_code == 400
    assert result == {"error": "No request data provided"}

def test_get_requests_by_staff_success(request_service, supabase_mock):
    supabase_response = MagicMock()
    supabase_response.data = [{"request_id": 1, "staff_id": "123"}]
    supabase_mock.from_("request").select().eq("staff_id", "123").execute.return_value = supabase_response

    result, status_code = request_service.get_requests_by_staff("123")
    assert status_code == 200
    assert result == [{"request_id": 1, "staff_id": "123"}]
    supabase_mock.from_("request").select().eq("staff_id", "123").execute.assert_called_once()

def test_get_requests_by_staff_not_found(request_service, supabase_mock):
    supabase_response = MagicMock()
    supabase_response.data = []
    supabase_mock.from_("request").select().eq("staff_id", "123").execute.return_value = supabase_response

    result, status_code = request_service.get_requests_by_staff("123")
    assert status_code == 404
    assert result == {"error": "No requests found for this staff ID"}
    supabase_mock.from_("request").select().eq("staff_id", "123").execute.assert_called_once()

def test_approve_request_success(request_service, supabase_mock):
    request_response = MagicMock()
    request_response.data = [{"request_id": 1, "staff_id": "123", "request_type": 1, "time_slot": "morning"}]
    supabase_mock.from_("request").select().eq("request_id", 1).execute.return_value = request_response

    request_service.create_schedule_entries = MagicMock()

    result = request_service.approve_request(1, "Approved", ["2024-11-01"])
    assert result == {"message": "Request approved successfully"}
    supabase_mock.from_("request").select().eq("request_id", 1).execute.assert_called_once()

def test_approve_request_not_found(request_service, supabase_mock):
    supabase_mock.from_("request").select().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    response = request_service.approve_request(999, "Approved", ["2023-01-01"])
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_mock.from_("request").select().eq("request_id", 999).execute.assert_called_once()

def test_reject_request_success(request_service, supabase_mock):
    supabase_response = MagicMock()
    supabase_response.data = True
    supabase_mock.from_("request").update().eq("request_id", 1).execute.return_value = supabase_response

    result = request_service.reject_request(1, "Not Approved")
    assert result == {"message": "Request rejected successfully"}
    supabase_mock.from_("request").update().eq("request_id", 1).execute.assert_called_once()

def test_reject_request_not_found(request_service, supabase_mock):
    supabase_mock.from_("request").update().eq("request_id", 999).execute.return_value = MagicMock(data=None)

    response = request_service.reject_request(999, "Rejected")
    assert response == ({'error': '404 Not Found: Request not found.'}, 500)
    supabase_mock.from_("request").update().eq("request_id", 999).execute.assert_called_once()

# ---------------------------------------------
# Testing RequestController
# ---------------------------------------------

def test_withdraw_request_controller_success(app, request_controller):
    with app.test_request_context():
        request_controller.request_service.withdraw_request = MagicMock(return_value=({"message": "Request withdrawn successfully"}, 200))
        
        # Call the controller method
        response = request_controller.withdraw_request(1)

        assert response.status_code == 200
        assert response.json == [{"message": "Request withdrawn successfully"}, response.status_code]

def test_cancel_request_controller_success(app, request_controller):
    with app.test_request_context():
        request_controller.request_service.cancel_request = MagicMock(return_value=({"message": "Request withdrawn successfully"}, 200))

        # Call the cancel_request method
        response = request_controller.cancel_request(1)

        # Assert that the response status code and data are correct
        assert response.status_code == 200
        assert response.json == [{"message": "Request withdrawn successfully"}, response.status_code]

def test_create_request_controller_success(app, request_controller):
    # Mock form data
    form_data = {
        'staffid': '123',
        'reason': 'Test Reason',
        'status': 'pending',
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 'morning',
        'request_type': 'vacation'
    }

    # Mock the request JSON data
    with app.test_request_context(json=form_data):
        # Mocking the request_service.create_request method
        mock_response = ({'request_id': '1', 'staff_id': '123'}, 201)
        request_controller.request_service.create_request = MagicMock(return_value=mock_response)

        # Call the controller method
        response, status_code = request_controller.create_request()

        # Flask response object should be tested
        assert status_code == 201
        assert response.get_json() == {'request_id': '1', 'staff_id': '123'}

def test_get_requests_by_staff_controller(app, request_controller):
    with app.test_request_context():
        # Mocking the service method
        mock_response = [{'request_id': '1', 'staff_id': '123'}], 200
        request_controller.request_service.get_requests_by_staff = MagicMock(return_value=mock_response)

        # Call the controller method
        response, status_code = request_controller.get_requests_by_staff("123")

        # Assert response and status code
        assert status_code == 200
        assert response.get_json() == [{'request_id': '1', 'staff_id': '123'}]

def test_get_team_requests_controller_success(app, request_controller):
    with app.test_request_context(headers={'X-Staff-ID': '123'}):
        request_controller.request_service.get_team_requests = MagicMock(return_value=(["request 1", "request 2"], 200))
        response, status_code = request_controller.get_team_requests()
        assert status_code == 200
        assert response.get_json() == ["request 1", "request 2"]

def test_approve_request_controller_success(app, request_controller):
    with app.test_request_context(json={
        "result_reason": "Approved",
        "approved_dates": ["2024-11-01"]
    }):
        request_controller.request_service.approve_request = MagicMock(return_value={"message": "Request approved successfully"})
        response = request_controller.approve_request(1)
        assert response.status_code == 200
        assert response.get_json() == {"message": "Request approved successfully"}

def test_reject_request_controller_success(app, request_controller):
    with app.test_request_context(json={
        "result_reason": "Not Approved"
    }):
        request_controller.request_service.reject_request = MagicMock(return_value={"message": "Request rejected successfully"})
        response = request_controller.reject_request(1)
        assert response.status_code == 200
        assert response.get_json() == {"message": "Request rejected successfully"}

def test_get_staff_id_missing_headers(app, request_controller):
    # Missing Authorization header
    with app.test_request_context(headers={'X-Staff-ID': '123'}):
        response = request_controller.get_staff_id()
        response_data = response.get_json()  # Extract the JSON data from the response
        assert response_data['staff_id'] == '123'
        assert response_data['access_token'] is None  # Should be None since Authorization is missing

    # Malformed Authorization header
    with app.test_request_context(headers={'X-Staff-ID': '123', 'Authorization': 'Bearer'}):
        response = request_controller.get_staff_id()
        response_data = response.get_json()
        assert response_data['staff_id'] == '123'
        assert response_data['access_token'] is None  # Token extraction should fail due to malformed header

    # Correct Authorization header
    with app.test_request_context(headers={'X-Staff-ID': '123', 'Authorization': 'Bearer some_token'}):
        response = request_controller.get_staff_id()
        response_data = response.get_json()
        assert response_data['staff_id'] == '123'
        assert response_data['access_token'] == 'some_token'
        
def test_create_request_database_insert_error(app, request_controller):
    request_service = request_controller.request_service
    # Mocking the database to return None (simulate failure)
    request_service.supabase.from_().insert().execute = MagicMock(return_value=None)

    with app.test_request_context(json={'staffid': '123', 'reason': 'Test'}):
        response, status_code = request_controller.create_request()
        response_data = response.get_json()  # Extract JSON from response
        assert status_code == 500
        assert response_data == {"error": "Failed to insert data into the database"}

def test_create_request_general_exception(app, request_controller):
    request_service = request_controller.request_service
    # Mocking to raise an exception
    request_service.supabase.from_().insert().execute = MagicMock(side_effect=Exception("Some error"))

    with app.test_request_context(json={'staffid': '123', 'reason': 'Test'}):
        response, status_code = request_controller.create_request()
        assert status_code == 500
        assert "Some error" in response.get_json()["error"]

def test_approve_request_success_controller(app, request_controller):
    request_service = request_controller.request_service
    # Mock supabase to simulate a successful request approval
    request_service.supabase.from_().select().eq().execute = MagicMock(return_value=MagicMock(data=[{'request_type': 1, 'time_slot': 1, 'staff_id': 123, 'request_id': 2}]))
    request_service.supabase.from_().update().eq().execute = MagicMock(return_value=MagicMock(data=[{}]))

    with app.test_request_context(json={'approved_dates': ['2024-01-01'], 'result_reason': 'Approved'}):
        response = request_controller.approve_request(123)
        assert response.status_code == 200
        assert response.get_json() == {"message": "Request approved successfully"}
