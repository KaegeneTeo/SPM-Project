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

def test_schedule_endpoint(client):
    with patch('flaskapp.models.schedules.SchedulesService.get_own_schedule') as get_own_mock, \
        patch('flaskapp.models.schedules.SchedulesService.get_schedules_by_reporting_manager') as get_schedules_mock:

        get_own_mock.return_value = MagicMock()
        get_schedules_mock.return_value = MagicMock()
        response = client.get('/schedule')
        assert get_own_mock.assert_called_once()
    assert response.get_json() == {"message": "Hello schedules"}