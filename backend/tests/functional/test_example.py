import pytest
from flask import jsonify
import json
from unittest.mock import MagicMock

def test_root_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_teams_by_reporting_manager(client, mocker):
    # Mock data for the initial staff query
    staff_mock_data = {
        "data": [
            {"Staff_ID": 1, "Staff_FName": "John", "Dept": "HR", "Position": "Manager", "Reporting_Manager": 2},
            {"Staff_ID": 2, "Staff_FName": "Jane", "Dept": "HR", "Position": "Director", "Reporting_Manager": 1}
        ]
    }

    # Mock data for the manager query
    manager_mock_data = {
        "data": [
            {"Staff_FName": "Doe"}
        ]
    }

    mock_supabase = MagicMock()
    mock_supabase.client.from_.return_value.select.return_value.execute.return_value = {
        "data": staff_mock_data,
    }

    # Patch the global supabase_extension with the mock version
    mocker.patch('flaskapp.main.supabase_extension', mock_supabase)

    # Call the `/teams_by_reporting_manager` route
    response = client.get('/teams_by_reporting_manager?department=HR')
    json_data = json.loads(response.data)

    # Assertions for the status code and data
    assert response.status_code == 200
    assert 'teams' in json_data
    assert len(json_data['teams']) > 0
    assert json_data['teams'][0]['manager_name'] == "Doe"  # Mocked manager name

# Test the /schedules route
def test_schedules(client, supabase_mock, mocker):
    mock_data = {
        "data": [
            {
                "Staff_ID": 1, "Staff_FName": "John", "Staff_LName": "Doe", "Dept": "HR",
                "schedule": [{"schedule_id": 1, "staff_id": 1, "date": "2024-10-14", "time_slot": 1}]
            }
        ]
    }
    mocker.patch('supabase.Client.from_').return_value.select.return_value.execute.return_value = mock_data

    response = client.get('/schedules?dept=all&reporting_manager=all&role=1')
    json_data = json.loads(response.data)

    assert response.status_code == 200
    assert len(json_data['schedules']) > 0
    assert json_data['schedules'][0]['class'] == "AM"

# Test the /login route
def test_login_route(client, supabase_mock, mocker):
    # Mock the login Supabase response
    mock_auth_response = mocker.Mock()
    mock_auth_response.user.email = "test@example.com"
    mock_auth_response.session.access_token = "mock_access_token"
    mock_auth_response.session.refresh_token = "mock_refresh_token"
    mocker.patch('supabase.Client.auth.sign_in_with_password').return_value = mock_auth_response

    # Mock the employee data returned by Supabase
    mock_employee_response = {
        "data": [
            {"Staff_ID": 1, "Role": "Admin", "Dept": "HR", "Reporting_Manager": 2}
        ]
    }
    mocker.patch('supabase.Client.table').return_value.select.return_value.ilike.return_value.execute.return_value = mock_employee_response

    # Call the login route
    response = client.post('/login', json={"email": "test@example.com", "password": "password"})

    # Assert the response
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['email'] == "test@example.com"
    assert json_data['access_token'] == "mock_access_token"
    assert json_data['staff_id'] == 1

# Test the /logout route
def test_logout_route(client, supabase_mock, mocker):
    mocker.patch('supabase.Client.auth.sign_out').return_value = None

    response = client.post('/logout')
    json_data = json.loads(response.data)

    assert response.status_code == 200
    assert json_data['message'] == "User signed out successfully."