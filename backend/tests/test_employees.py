import pytest
from unittest.mock import MagicMock
from flask import Flask, jsonify, request
from flaskapp.models.employees import EmployeesService, EmployeesController
from unittest.mock import patch, Mock

@pytest.fixture
def app():
    app = Flask(__name__)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def supabase_mock():
    return MagicMock()

@pytest.fixture
def employees_service(supabase_mock):
    return EmployeesService(supabase_mock)

@pytest.fixture
def employees_controller(employees_service):
    return EmployeesController(employees_service)

### Unit Tests for EmployeesService

def test_get_all_employees(employees_service, supabase_mock):
    # Mocking the response from the supabase client
    supabase_mock.from_().select().execute.return_value.data = [{"Staff_ID": 1, "Name": "John Doe"}]

    result = employees_service.get_all_employees()

    # Verifying the method works correctly
    assert result == [{"Staff_ID": 1, "Name": "John Doe"}]
    supabase_mock.from_().select().execute.assert_called_once()

def test_update_employee(employees_service, supabase_mock):
    # Mocking the response for update
    form_data = {"Name": "John Doe Updated"}
    supabase_mock.from_().update().eq().execute.return_value.status_code = 200

    result = employees_service.update_employee(1, form_data)

    assert result.status_code == 200
    supabase_mock.from_().update().eq().execute.assert_called_once()

def test_get_staff_id_from_headers(employees_service, supabase_mock):
    # Mocking the supabase client response for fetching staff by ID
    supabase_mock.from_().select().eq().execute.return_value.data = [{"Staff_ID": 1, "Name": "John Doe"}]

    result = employees_service.get_staff_id_from_headers(1)

    assert result == [{"Staff_ID": 1, "Name": "John Doe"}]
    supabase_mock.from_().select().eq().execute.assert_called_once()

### Unit Tests for EmployeesController

def test_check_online(employees_controller):
    response = employees_controller.check_online()
    assert response == ("Hello employees", 200)

def test_get_employees(client, employees_controller):
    # Mock only the service call
    mock_response = [{"Staff_ID": 1, "Name": "John Doe"}]
    
    with patch.object(employees_controller.employees_service, 'get_all_employees', return_value=mock_response):
        # Execute the controller method
        with client.application.test_request_context():
            response, status_code = employees_controller.get_employees()
        
    # Assertions (this ensures the logic is executed)
    assert status_code == 200
    assert response.get_json() == mock_response

def test_update_employee_success(client, employees_controller):
    # Mocking form data and headers
    mock_response = Mock()
    mock_response.status_code = 200

    with patch.object(employees_controller.employees_service, 'update_employee', return_value=mock_response):
        headers = {'X-Staff-ID': '1'}
        form_data = {'Name': 'John Doe Updated'}
        
        with client.application.test_request_context(headers=headers, data=form_data):
            response, status_code = employees_controller.update_employee()

    assert status_code == 200
    assert response.get_json() == {"message": "Employee updated successfully"}

def test_update_employee_failure(client, employees_controller):
    # Mocking failure case
    mock_response = Mock()
    mock_response.status_code = 500

    with patch.object(employees_controller.employees_service, 'update_employee', return_value=mock_response):
        headers = {'X-Staff-ID': '1'}
        form_data = {'Name': 'John Doe Updated'}

        with client.application.test_request_context(headers=headers, data=form_data):
            response, status_code = employees_controller.update_employee()

    assert status_code == 500
    assert response.get_json() == {"error": "Failed to update employee"}

def test_get_staff_id_success(client, employees_controller):
    # Mocking successful token and staff ID retrieval
    mock_staff_details = [{"Staff_ID": 1, "Name": "John Doe"}]
    
    with patch.object(employees_controller.employees_service, 'get_staff_id_from_headers', return_value=mock_staff_details):
        headers = {'X-Staff-ID': '1', 'Authorization': 'Bearer valid_token'}

        with client.application.test_request_context(headers=headers):
            response, status_code = employees_controller.get_staff_id()

    assert status_code == 200
    assert response.get_json() == {
        "message": "CORS is working",
        "staff_id": '1',
        "access_token": 'valid_token',
        "staff_details": mock_staff_details
    }
def test_get_staff_id_failure(client, employees_controller):
    # Mocking missing headers
    headers = {}

    with client.application.test_request_context(headers=headers):
        response, status_code = employees_controller.get_staff_id()

    assert status_code == 400
    assert response.get_json() == {"error": "Staff ID and token are required"}
