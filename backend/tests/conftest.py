import pytest
from app import app
import os
from supabase import create_client, Client

@pytest.fixture()
def client():
    with app.test_client() as client:   
        yield client