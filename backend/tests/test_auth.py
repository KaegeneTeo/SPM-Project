from flaskapp.models.auth import AuthService
from flaskapp.extensions import supabase
from unittest.mock import patch
from flask import Response
import json

# Test login success
def test_login_success(client):
    auth_service = AuthService(supabase)

    # Use real credentials from your test setup
    response, status_code = auth_service.login('Eric.Loh@allinone.com.sg', '123')

    assert status_code == 200
    assert 'email' in response
    assert response['email'] == 'Eric.Loh@allinone.com.sg'
    assert 'access_token' in response
    assert 'staff_id' in response

# Test login failure with wrong password
def test_login_failure(client):
    auth_service = AuthService(supabase)

    # This should return a failure with invalid credentials
    response, status_code = auth_service.login('test@example.com', 'wrong_password')

    assert status_code == 400
    assert 'message' in response
    assert 'Invalid login credentials' in response['message']

# Test check auth with valid token
def test_check_auth_success(client):
    auth_service = AuthService(supabase)
    mock_user_data = {
        "user": {
            "email": "test@example.com",
            "role": "admin",
        },
        "session": {
            "access_token": "mocked_token",
            "refresh_token": "mocked_token"
        }
    }
    

    with patch('flaskapp.extensions.supabase.auth.get_user', return_value=mock_user_data):
        

        response, status_code = auth_service.check_auth("mocked_token")
        assert status_code == 200
    
        assert 'email' in response

# Test check auth with invalid token
def test_check_auth_failure(client):
    auth_service = AuthService(supabase)

    # Use an invalid token
    invalid_token = "invalid_token_here"
    response, status_code = auth_service.check_auth(invalid_token)

    assert status_code == 400
    assert 'message' in response
    assert 'invalid JWT' in response['message']
# Test logout
def test_logout_success(client):
    auth_service = AuthService(supabase)

    response, status_code = auth_service.logout()

    assert status_code == 200
    assert response['message'] == "User signed out successfully."



def test_login_route(client):
    response = client.post('/login', json={
        'email': 'Eric.Loh@allinone.com.sg',
        'password': '123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'email' in data
    assert data['email'] == 'Eric.Loh@allinone.com.sg'
    assert 'access_token' in data

def test_login_route_failure(client):
    response = client.post('/login', json={
        'email': 'Eric.Loh@allinone.com.sg',
        'password': 'wrong_password'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert 'Invalid login credentials' in data['message']

#def test_check_auth_route(client):
#    # Use a valid access token from your test database
#    mock_user_data = {
#        "user": {
#            "email": "test@example.com",
#            "role": "admin",
#            "access_token": "mocked_token",
#            "refresh_token": "mocked_token"
#        }
#    }
#    with patch('flaskapp.extensions.supabase.auth.get_user', return_value=mock_user_data):
#        
#        # Simulate a POST request to the check_auth route
#        response = client.post('/check_auth', data={'access_token': 'mocked_token'})
#        
#        assert response.status_code == 200
#        data = response.get_json()
#        assert data['email'] == "test@example.com"
#        assert data['role'] == "admin"

def test_logout_route(client):
    response = client.post('/logout')

    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == "User signed out successfully."

