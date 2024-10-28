import pytest
from unittest.mock import MagicMock
from flask import Flask, jsonify, request
from flaskapp.models.notification import notification_engine, notification_sender, supabase_access
import requests
from unittest import mock

#setup
@pytest.fixture
def supabase_mock():
    return MagicMock()

@pytest.fixture
def supabase_caller(supabase_mock):
    return supabase_access(supabase_mock)

@pytest.fixture
def notif_engine(supabase_caller):
    return notification_engine(supabase_caller)

@pytest.fixture
def notif_sender(notif_engine):
    return notification_sender(notif_engine)

#happy paths
def test_get_request_data(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = [{
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}]
    assert supabase_caller.get_request_data(1) == ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200)

def test_get_staff_data(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = [{
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2}]
    assert supabase_caller.get_staff_data(1) == ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2}, 200)
    
def test_get_latest_req(supabase_caller):
    supabase_caller.supabase.from_().select().order().limit().execute.return_value.data = [{
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}]
    assert supabase_caller.get_latest_req() == ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200)

def test_get_manager_data(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = [{
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1}]
    assert supabase_caller.get_manager_data(1) == ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1}, 200)

def test_compose_approve(notif_engine, supabase_caller): 
    supabase_caller.get_request_data = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    assert notif_engine.compose_approve(1) == ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been partially or fully approved. Please check your schedule for details.", 200)

def test_compose_reject(supabase_caller, notif_engine):
    supabase_caller.get_request_data = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    assert notif_engine.compose_reject(1) == ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been rejected.", 200)

def test_compose_create(supabase_caller, notif_engine):
    supabase_caller.get_latest_req = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_create() == ("Hi Jane Doe, John Doe has sent a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200)

#data for input input compose cancel and compose withdraw
data = {
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}

def test_compose_cancel(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_cancel(data) == ("Hi Jane Doe, John Doe has cancelled a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200)

def test_compose_withdraw(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_withdraw(data) == ("Hi Jane Doe, John Doe has withdrawn a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200)

#error paths

#bad DB calls
def test_get_request_data_error(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = None
    assert supabase_caller.get_request_data(1) == ({"error": "Requests not found"}, 404)

def test_get_staff_data_error(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = None
    assert supabase_caller.get_staff_data(1) == ({"error": "Employee not found"}, 404)
    
def test_get_latest_req_error(supabase_caller):
    supabase_caller.supabase.from_().select().order().limit().execute.return_value.data = None
    assert supabase_caller.get_latest_req() == ({"error": "Requests not found"}, 404)

def test_get_manager_data_error(supabase_caller):
    supabase_caller.supabase.from_().select().eq().execute.return_value.data = None
    assert supabase_caller.get_manager_data(1) == ({"error": "Employee not found"}, 404)

#-ve compose approve
def test_compose_approve_request_data_error(supabase_caller, notif_engine):
    supabase_caller.get_request_data = MagicMock(return_value = ({"error": "Request not found"}, 404))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    assert notif_engine.compose_approve(1) == ("Error fetching request", 500)

def test_compose_approve_staff_data_error(supabase_caller, notif_engine):
    supabase_caller.get_request_data = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({"error": "Staff not found"}, 404))
    assert notif_engine.compose_approve(1) == ("Error fetching staff", 500)

#-ve compose reject
def test_compose_reject_request_data_error(supabase_caller, notif_engine):
    supabase_caller.get_request_data = MagicMock(return_value = ({"error": "Request not found"}, 404))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    assert notif_engine.compose_reject(1) == ("Error fetching request", 500)

def test_compose_reject_staff_data_error(supabase_caller, notif_engine):
    supabase_caller.get_request_data = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({"error": "Staff not found"}, 404))
    assert notif_engine.compose_reject(1) == ("Error fetching staff", 500)

#-ve compose create
def test_compose_create_req_data_error(supabase_caller, notif_engine):
    supabase_caller.get_latest_req = MagicMock(return_value = ({"error": "Request not found"}, 404))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_create() == ("Error fetching request", 500)

def test_compose_create_staff_data_error(supabase_caller, notif_engine):
    supabase_caller.get_latest_req = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({"error": "Employee not found"}, 404))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_create() == ("Error fetching staff", 500)

def test_compose_create_manager_data_error(supabase_caller, notif_engine):
    supabase_caller.get_latest_req = MagicMock(return_value = ({
        "request_id": 1, 
        "staff_id": 1, 
        "reason": "test", 
        "status": 1, 
        "startdate": "1970-1-1", 
        "enddate": "1970-1-2", 
        "time_slot": 3, 
        "request_type": 1, 
        "result_reason": None}, 200))
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({"error": "Employee not found"}, 404))
    assert notif_engine.compose_create() == ("Error fetching manager", 500)

#-ve compose cancel w/o bad data input
def test_compose_cancel_staff_data_error(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({"error": "Employee not found"}, 404))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_cancel(data) == ("Error fetching staff", 500)

def test_compose_cancel_manager_data_error(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({"error": "Employee not found"}, 404))
    assert notif_engine.compose_cancel(data) == ("Error fetching manager", 500)

#-ve compose withdraw w/o bad data input
def test_compose_withdraw_staff_data_error(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({"error":"Employee not found"}, 404))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_withdraw(data) == ("Error fetching staff", 500)

def test_compose_withdraw_manager_data_error(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({"error":"Employee not found"}, 404))
    assert notif_engine.compose_withdraw(data) == ("Error fetching manager", 500)

#bad input
baddata = {}

#compose withdraw and cancel with bad input
def test_compose_cancel_bad_data(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_cancel(baddata) == ("Erroneous arguments submitted", 500)

def test_compose_withdraw_bad_data(supabase_caller, notif_engine):
    supabase_caller.get_staff_data = MagicMock(return_value = ({
        "Staff_ID":1,
        "Staff_FName":"John",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Manager",
        "Country":"Singapore",
        "Email":"john.doe@allinone.com.sg",
        "Reporting_Manager":2,
        "Role":2
    }, 200))
    supabase_caller.get_manager_data = MagicMock(return_value = ({
        "Staff_ID":2,
        "Staff_FName":"Jane",
        "Staff_LName":"Doe",
        "Dept":"Sales",
        "Position":"Sales Director",
        "Country":"Singapore",
        "Email":"jane.doe@allinone.com.sg",
        "Reporting_Manager":3,
        "Role":1
    }, 200))
    assert notif_engine.compose_withdraw(baddata) == ("Erroneous arguments submitted", 500)

#test senders

#happy path
def test_send_approve(notif_engine, notif_sender):
    notif_engine.compose_approve = MagicMock(return_value = ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been partially or fully approved. Please check your schedule for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_approve(1) == 200

def test_send_reject(notif_engine, notif_sender):
    notif_engine.compose_reject = MagicMock(return_value = ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been rejected.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_reject(1) == 200

def test_send_created(notif_engine, notif_sender):
    notif_engine.compose_create = MagicMock(return_value = ("Hi Jane Doe, John Doe has sent a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_create() == 200

def test_send_cancel(notif_engine, notif_sender):
    notif_engine.compose_cancel = MagicMock(return_value = ("Hi Jane Doe, John Doe has cancelled a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_cancel(data) == 200

def test_send_withdraw(notif_engine, notif_sender):
    notif_engine.compose_withdraw = MagicMock(return_value = ("Hi Jane Doe, John Doe has withdrawn a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_withdraw(data) == 200

#-ve path error from compose
def test_send_approve_compose_error(notif_engine, notif_sender):
    notif_engine.compose_approve = MagicMock(return_value = ("Unique error1", 500))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_approve(1) == "Unique error1"

def test_send_reject_compose_error(notif_engine, notif_sender):
    notif_engine.compose_reject = MagicMock(return_value = ("Unique error2", 500))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_reject(1) == "Unique error2"

def test_send_created_compose_error(notif_engine, notif_sender):
    notif_engine.compose_create = MagicMock(return_value = ("Unique error3", 500))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_create() == "Unique error3"

def test_send_cancel_compose_error(notif_engine, notif_sender):
    notif_engine.compose_cancel = MagicMock(return_value = ("Unique error4", 500))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_cancel(data) == "Unique error4"

def test_send_withdraw_compose_error(notif_engine, notif_sender):
    notif_engine.compose_withdraw = MagicMock(return_value = ("Unique error5", 500))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 200
        assert notif_sender.send_withdraw(data) == "Unique error5"

#post error path
def test_send_approve_post_error(notif_engine, notif_sender):
    notif_engine.compose_approve = MagicMock(return_value = ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been partially or fully approved. Please check your schedule for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 400
        assert notif_sender.send_approve(1) == "Email failed to send"

def test_send_reject_post_error(notif_engine, notif_sender):
    notif_engine.compose_reject = MagicMock(return_value = ("Hi John Doe, your request (ID: 1) from 1970-1-1 to 1970-1-2 has been rejected.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 400
        assert notif_sender.send_reject(1) == "Email failed to send"

def test_send_created_post_error(notif_engine, notif_sender):
    notif_engine.compose_create = MagicMock(return_value = ("Hi Jane Doe, John Doe has sent a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 400
        assert notif_sender.send_create() == "Email failed to send"

def test_send_cancel_post_error(notif_engine, notif_sender):
    notif_engine.compose_cancel = MagicMock(return_value = ("Hi Jane Doe, John Doe has cancelled a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 400
        assert notif_sender.send_cancel(data) == "Email failed to send"

def test_send_withdraw_post_error(notif_engine, notif_sender):
    notif_engine.compose_withdraw = MagicMock(return_value = ("Hi Jane Doe, John Doe has withdrawn a request (ID: 1) from 1970-1-1 to 1970-1-2. Please check requests for details.", 200))
    with mock.patch('requests.post') as patched_post:
        patched_post.return_value.status_code = 400
        assert notif_sender.send_withdraw(data) == "Email failed to send"