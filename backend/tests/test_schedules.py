import pytest
from flask import jsonify
from unittest.mock import MagicMock, patch
from flaskapp.models.schedules import SchedulesService

@pytest.fixture
def supabase_mock():
    return MagicMock()

@pytest.fixture
def schedules_service(supabase_mock):
    return SchedulesService(supabase_mock)

@pytest.fixture
def schedules_service_mock():
    # Mock the SchedulesService class methods
    mocker = MagicMock()
    mock = mocker.patch('flaskapp.models.schedules.SchedulesService')
    return mock

# Test case for getting the own schedule of a staff member
def test_get_own_schedule(schedules_service, supabase_mock):
    staff_id = 1
    position = "Sales Manager"
    dept = "Sales"
    staff_fname = "John"
    staff_lname = "Doe"
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': staff_id, 'Position': position, "Dept": dept, 'Staff_FName': staff_fname, 'Staff_LName': staff_lname, 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_own_schedule(staff_id)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)')
    select_mock.eq.assert_called_once_with('Staff_ID', staff_id)

# Test case for getting the CEO's staff ID
def test_get_ceo(schedules_service, supabase_mock):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 2}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_ceo()
    
    assert result == 2
    supabase_mock.from_().select.assert_called_once_with('Staff_ID')
    select_mock.eq.assert_called_once_with("Position", "MD")

# Test case for getting all employees
def test_get_all_employees(schedules_service, supabase_mock):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Dept": "Sales", "Position": "Sales_Manager"}]
    
    select_mock = MagicMock()
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_all_employees()
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position')

# Test case for getting schedules for all departments
def test_get_schedules_for_all_depts(schedules_service, supabase_mock):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': "John", 'Staff_LName': "Doe", 'Position': "HR_Manager", 'Dept': 'HR', 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    select_mock = MagicMock()
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_schedules_for_all_depts()
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)')

# Test case for getting employees by department
def test_get_all_employees_by_dept(schedules_service, supabase_mock):
    dept = "HR"
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Position":'HR_Manager', "Dept":"HR"}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_all_employees_by_dept(dept)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position')
    select_mock.eq.assert_called_once_with("Dept", dept)

# Test case for getting schedules by department
def test_get_schedules_by_dept(schedules_service, supabase_mock):
    dept = "HR"
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', 'Dept': dept, "Position": "HR_Manager", 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_schedules_by_dept(dept)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)')
    select_mock.eq.assert_called_once_with("Dept", dept)

# Test case for getting schedules by reporting manager
def test_get_schedules_by_reporting_manager(schedules_service, supabase_mock):
    dept = "HR"
    reporting_manager = 1
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Dept': dept, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Position": "HR_Manager", 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_schedules_by_reporting_manager(dept, reporting_manager)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)')
    select_mock.eq.assert_any_call("Dept", dept)

# Test case for getting employees by reporting manager
def test_get_all_employees_by_reporting_manager(schedules_service, supabase_mock):
    dept = "HR"
    reporting_manager = 1
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Dept': dept, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Position": "HR_Manager"}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_all_employees_by_reporting_manager(dept, reporting_manager)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position')
    select_mock.eq.assert_any_call("Dept", dept)

# Test case for getting all directors
def test_get_all_directors(schedules_service, supabase_mock):
    reporting_manager = 1
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Dept": "HR", "Position": "Director"}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.neq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_all_directors(reporting_manager)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position')

# Test case for getting directors' schedules
def test_get_directors_schedules(schedules_service, supabase_mock):
    reporting_manager = 1
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1,'Staff_FName': 'John', 'Staff_LName': 'Doe', "Position": "Director", 'Dept': 'HR', 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    select_mock = MagicMock()
    select_mock.eq.return_value = select_mock
    select_mock.neq.return_value = select_mock
    select_mock.execute.return_value = mock_response
    supabase_mock.from_().select.return_value = select_mock

    result = schedules_service.get_directors_schedules(reporting_manager)
    
    assert result.data == mock_response.data
    supabase_mock.from_().select.assert_called_once_with('Staff_ID, Staff_FName, Staff_LName, Dept, Position, schedule!inner(schedule_id, staff_id, date, time_slot)')

# Test case for formatting schedules
def test_format_schedules(schedules_service):
    response = MagicMock()
    response.data = [{'Staff_ID': 1, 'Dept': 'HR', 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Position": "HR_Manager", 'schedule': [{'schedule_id': 1, 'date': '2024-10-16', 'time_slot': 1}]}]
    
    allnames = MagicMock()
    allnames.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', "Dept": "HR", "Position": "HR_Manager"}]
    
    result, status_code = schedules_service.format_schedules(response, allnames)
    assert result == {'schedules': [{'start': '2024-10-16 09:00', 'end': '2024-10-16 13:00', 'class': 'AM', 'WFH': ['1 - John Doe - HR - HR_Manager'], 'count': 1, 'title': 1, 'inOffice': []}]}
    assert status_code == 200

# Test case for formatting schedules with no data
def test_format_schedules_no_data(schedules_service):
    response = MagicMock()
    response.data = None
    
    allnames = MagicMock()
    allnames.data = []
    
    result, status_code = schedules_service.format_schedules(response, allnames)
    assert result == {'code': 404, 'message': 'No data or bad data'}
    assert status_code == 404


def test_get_schedules_own_schedule(client):
    # Use the `patch` context manager and capture the mock objects
    with patch('flaskapp.models.schedules.SchedulesService.get_own_schedule') as mock_get_own_schedule, \
         patch('flaskapp.models.schedules.SchedulesService.get_schedules_by_reporting_manager') as mock_get_schedules_by_reporting_manager:

        # Mock the return values of the patched methods
        mock_get_own_schedule.return_value = {}
        mock_get_schedules_by_reporting_manager.return_value = {}

        # Make the request
        response = client.get('/schedules', query_string={
            'staff_id': '1',
            'dept': 'HR',
            'reporting_manager': '2'
        })

        # Assertions on response status code, etc.
        assert response.status_code == 200

        # Use assert_called_once_with to check if the methods were called with specific arguments
        mock_get_own_schedule.assert_called_once_with('1')
        mock_get_schedules_by_reporting_manager.assert_called_once_with('HR', 2)

def test_get_schedules_ceo(client):
    # Mock the get_ceo, get_all_employees_by_dept, and get_schedules_by_dept methods

    with patch('flaskapp.models.schedules.SchedulesService.get_ceo') as mock_get_ceo, \
         patch('flaskapp.models.schedules.SchedulesService.get_all_employees_by_dept') as mock_get_all_employees_by_dept, \
         patch('flaskapp.models.schedules.SchedulesService.get_schedules_by_dept') as mock_get_schedules_by_dept:

        # Mock the return values of the patched methods
        mock_get_ceo.return_value = {}
        mock_get_all_employees_by_dept.return_value = {}
        mock_get_schedules_by_dept.return_value = {}

        # Call the endpoint with dept set to CEO
        response = client.get('/schedules', query_string={
            'dept': 'CEO',
            'reporting_manager': 'all'
        })

        # Verify that the service methods were called correctly
        mock_get_ceo.assert_called_once()
        mock_get_all_employees_by_dept.assert_called_once_with('CEO')
        mock_get_schedules_by_dept.assert_called_once_with('CEO')

        # Verify the response status code
        assert response.status_code == 200

def test_get_schedules_all_depts(client):

    # Mock the get_all_employees and get_schedules_for_all_depts methods
    with patch('flaskapp.models.schedules.SchedulesService.get_all_employees') as mock_get_all_employees, \
         patch('flaskapp.models.schedules.SchedulesService.get_schedules_for_all_depts') as mock_get_schedules_for_all_depts:

        # Mock the return values of the patched methods
        mock_get_all_employees.return_value = {}
        mock_get_schedules_for_all_depts.return_value = {}
        # Call the endpoint with dept=all and reporting_manager=all
        response = client.get('/schedules', query_string={
            'dept': 'all',
            'reporting_manager': 'all'
        })

        mock_get_all_employees.assert_called_once()
        mock_get_schedules_for_all_depts.assert_called_once()
        assert response.status_code == 200


def test_get_schedules_for_team_in_dept(client):
    # Mock the get_all_employees_by_dept and get_schedules_by_dept methods
    with patch('flaskapp.models.schedules.SchedulesService.get_all_employees_by_dept') as mock_get_all_employees_by_dept, \
         patch('flaskapp.models.schedules.SchedulesService.get_schedules_by_dept') as mock_get_schedules_by_dept:

        # Call the endpoint with a specific department and reporting_manager=all
        response = client.get('/schedules', query_string={
            'dept': 'IT',
            'reporting_manager': 'all'
        })

        # Verify that the service methods were called correctly
        mock_get_all_employees_by_dept.assert_called_once_with('IT')
        mock_get_schedules_by_dept.assert_called_once_with('IT')
        # Verify the response status code
        assert response.status_code == 200

def test_get_schedules_directors_team(client):
    # Mock the get_all_directors and get_directors_schedules methods
    with patch('flaskapp.models.schedules.SchedulesService.get_all_directors') as mock_get_all_directors, \
         patch('flaskapp.models.schedules.SchedulesService.get_directors_schedules') as mock_get_directors_schedules, \
        patch('flaskapp.models.schedules.SchedulesService.get_ceo') as mock_get_ceo:
        
        # Mock the return values of the patched methods
        mock_get_all_directors.return_value = {}
        mock_get_directors_schedules.return_value = {}
        mock_get_ceo.return_value = 1
        # Call the endpoint with the role and reporting_manager of the CEO
        response = client.get('/schedules', query_string={
            'role': '1',
            'reporting_manager': '1',  # Mocking the CEO ID as 1
            'dept': 'IT'
        })

        mock_get_all_directors.assert_called_once_with("1")
        mock_get_directors_schedules.assert_called_once_with("1")
        assert response.status_code == 200

def test_get_schedules_by_dept_and_reporting_manager(client, schedules_service_mock):
    # Mock the get_schedules_by_reporting_manager and get_all_employees_by_reporting_manager methods
    with patch('flaskapp.models.schedules.SchedulesService.get_schedules_by_reporting_manager') as mock_get_schedules_by_reporting_manager, \
        patch('flaskapp.models.schedules.SchedulesService.get_all_employees_by_reporting_manager') as mock_get_all_employees_by_reporting_manager, \
        patch('flaskapp.models.schedules.SchedulesService.get_ceo') as mock_get_ceo:

        mock_get_all_employees_by_reporting_manager.return_value = {}
        mock_get_schedules_by_reporting_manager.return_value = {}
        mock_get_ceo.return_value = 1
        # Call the endpoint with a specific department and reporting manager
        response = client.get('/schedules', query_string={
            'dept': 'IT',
            'reporting_manager': '2',
            'role': '1'
        })
        
        mock_get_all_employees_by_reporting_manager.assert_called_once_with('IT', 2)
        mock_get_schedules_by_reporting_manager.assert_called_once_with('IT', 2)
        assert response.status_code == 200

def test_get_schedules_missing_params(client, schedules_service_mock):
    # Call the endpoint without providing necessary query parameters
    response = client.get('/schedules', query_string={})

    # Verify that no service methods were called and an error is returned
    schedules_service_mock.get_own_schedule.assert_not_called()
    schedules_service_mock.get_schedules_for_all_depts.assert_not_called()

    assert response.status_code == 400  

def test_format_schedules_if_branch(schedules_service):
    # Mock response with unique date-time combinations
    response_mock = MagicMock()
    response_mock.data = [
        {
            "Dept": "HR",
            "Staff_FName": "John",
            "Staff_LName": "Doe",
            "Staff_ID": 1,
            "Position": "Analyst",
            "schedule": [{"date": "2023-10-01", "schedule_id": 101, "time_slot": 1}]
        }
    ]

    allnames_mock = MagicMock()
    allnames_mock.data = response_mock.data  # Simulate the allnames data for this case

    # Call format_schedules
    result, status = schedules_service.format_schedules(response_mock, allnames_mock)

    # Assertions
    assert status == 200
    assert len(result["schedules"]) == 1
    assert result["schedules"][0]["WFH"] == ["1 - John Doe - HR - Analyst"]

def test_format_schedules_else_branch(schedules_service):
    # Mock response with a duplicate date-time combination to trigger else
    response_mock = MagicMock()
    response_mock.data = [
        {
            "Dept": "HR",
            "Staff_FName": "John",
            "Staff_LName": "Doe",
            "Staff_ID": 1,
            "Position": "Analyst",
            "schedule": [{"date": "2023-10-01", "schedule_id": 101, "time_slot": 1}]
        },
        {
            "Dept": "IT",
            "Staff_FName": "Jane",
            "Staff_LName": "Smith",
            "Staff_ID": 2,
            "Position": "Developer",
            "schedule": [{"date": "2023-10-01", "schedule_id": 102, "time_slot": 1}]
        }
    ]

    allnames_mock = MagicMock()
    allnames_mock.data = response_mock.data  # Simulate the allnames data for this case

    # Call format_schedules
    result, status = schedules_service.format_schedules(response_mock, allnames_mock)

    # Assertions
    assert status == 200
    assert len(result["schedules"]) == 1  # Same date and time slot are combined
    assert len(result["schedules"][0]["WFH"]) == 2
    assert "1 - John Doe - HR - Analyst" in result["schedules"][0]["WFH"]
    assert "2 - Jane Smith - IT - Developer" in result["schedules"][0]["WFH"]