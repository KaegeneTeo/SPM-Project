import pytest
from app import create_app
import os
from supabase import create_client, Client
import json
from flaskapp.app import create_app

@pytest.fixture()
def app():
    app = create_app()
    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()