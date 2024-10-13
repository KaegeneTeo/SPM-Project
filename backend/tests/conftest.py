import pytest
from app import create_app
import os
from supabase import create_client, Client
import json
from app import app as app

@pytest.fixture()
def app():

    # other setup can go here
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()