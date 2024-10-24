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

# ---------------------------------------------
# Testing RequestService
# ---------------------------------------------

def test_withdraw_request_success(request_service, supabase_client):
    # Mock the response for withdrawing a request
    supabase_client.from_("request").delete().eq("request_id", 1).execute.return_value = MagicMock(data=True)
    
    response_data, status_code = request_service.withdraw_request(1)
    
    assert status_code == 200
    assert response_data == {"message": "Request withdrawn successfully"}
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
    assert status_code == 200
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
    mock_data = {'request_id': 1}

    # Mock the withdraw_request method in the RequestService
    with patch.object(request_controller.request_service, 'withdraw_request', return_value=(mock_response, mock_data)):
        response = client.delete('/withdraw_request/1')

    assert response.status_code == 200
    assert response.get_json() == mock_response

    # with app.test_request_context():
    #     request_controller.request_service.withdraw_request = MagicMock(return_value=({"message": "Request withdrawn successfully"}, 200))
        
    #     # Call the controller method
    #     response = request_controller.withdraw_request(1)

    #     assert response.status_code == 200
    #     assert response.json == [{"message": "Request withdrawn successfully"}, response.status_code]
def test_withdraw_request_controller_failure(request_controller, client):
    mock_response = {'error': 'Request not found'}
    
    with patch.object(request_controller, 'withdraw_request', return_value=(mock_response, None)):
        response = client.delete('/withdraw_request/999')  # Non-existent request
        
    assert response.status_code == 404
    assert response.get_json() == mock_response

def test_cancel_request_controller_success(request_controller, client):
    mock_response = {"message": "Request withdrawn successfully"}
    mock_data = {'request_id': 2}
    
    with patch.object(request_controller.request_service, 'cancel_request', return_value=(mock_response, mock_data)):
        response = client.delete('/cancel_request/2')
        
    assert response.status_code == 200
    assert response.get_json() == mock_response

def test_cancel_request_controller_failure(request_controller, client):
    mock_response = {'error': 'Request not found'}
    
    with patch.object(request_controller, 'cancel_request', return_value=(mock_response, None)):
        response = client.delete('/cancel_request/999')  # Non-existent request
        
    assert response.status_code == 404
    assert response.get_json() == mock_response

def test_create_request_controller_success(request_controller, client):
    form_data = {
        'staffid': '123',
        'reason': 'Test Reason',
        'status': 'pending',
        'startdate': '2023-01-01',
        'enddate': '2023-01-02',
        'time_slot': 'morning',
        'request_type': 'vacation'
    }

    # Mock the request_service.create_request method
    mock_response = ({'request_id': '1', 'staff_id': '123'}, 201)
    with patch.object(request_controller.request_service, 'create_request', return_value=mock_response):
        # Send a POST request to the endpoint with JSON data
        response = client.post('/requests/', json=form_data)

    # Assert the response
    assert response.status_code == 201  # Make sure you're asserting the correct status code
    assert response.get_json() == {'request_id': '1', 'staff_id': '123'}

def test_create_request_controller_failure(request_controller, client):
    mock_response = {'error': 'Invalid request data'}
    
    with patch.object(request_controller, 'create_request', return_value=mock_response):
        response = client.post('/requests/')  # Simulate a bad request
        
    assert response.status_code == 400
    assert response.get_json() == mock_response

def test_get_requests_by_staff_controller(request_controller, client):
    mock_response = [{'request_id': '1', 'staff_id': '123'}]
    
    with patch.object(request_controller.request_service, 'get_requests_by_staff', return_value=(mock_response, 200)):
        response = client.get('/requests/123')  # Adjust the endpoint based on your routing
        assert response.status_code == 200
        assert response.get_json() == mock_response

def test_get_team_requests_controller_success(request_controller, client):
    with patch.object(request_controller.request_service, 'get_team_requests', return_value=(["request 1", "request 2"], 200)):
        response = client.get('/team/requests')  # Adjust the endpoint based on your routing
        assert response.status_code == 200
        assert response.get_json() == ["request 1", "request 2"]

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
            assert response.status_code == 200
            assert response.get_json() == {"message": "Request rejected successfully"}

def test_get_staff_id_missing_authorization(client):
    # Missing Authorization header
    response = client.get('/getstaffid', headers={'X-Staff-ID': '123'})
    response_data = response.get_json()

    # Assert that the response contains the error for missing Authorization
    assert 'error' in response_data
    assert response_data['error'] == 'Staff ID and token are required'
    
def test_get_staff_id_missing_staff_id(client):
    # Missing X-Staff-ID header
    response = client.get('/getstaffid', headers={'Authorization': 'Bearer some_token'})
    response_data = response.get_json()

    # Assert that the response contains the error for missing Staff ID
    assert 'error' in response_data
    assert response_data['error'] == 'Staff ID and token are required'

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
        
def test_create_request_database_insert_error(request_controller, client):
    # Mocking the database to raise an exception (simulate failure)
    with patch.object(request_controller.request_service.supabase.from_(), 'insert') as mock_insert:
        mock_insert.return_value.execute.side_effect = Exception("Null value in column 'status' violates not-null constraint")

        response = client.post('/requests/', json={'staffid': '123', 'reason': 'Test'})
        response_data = response.get_json()  # Extract JSON from response
        
        # Assert the expected status code and error message
        assert response.status_code == 500
        #assert response_data == {"error": "Failed to insert data into the database"}

def test_create_request_general_exception(request_controller, client):
    # Mocking to raise a general exception
    with patch.object(request_controller.request_service.supabase.from_(), 'insert') as mock_insert:
        # Setting the insert to raise an exception when execute is called
        mock_insert.return_value.execute.side_effect = Exception("Some error")
        
        response = client.post('/requests/', json={'staffid': '123', 'reason': 'Test'})
        
        # Assert the expected status code and error message
        assert response.status_code == 500
        #assert response.get_json()["error"] == "Failed to insert data into the database"

