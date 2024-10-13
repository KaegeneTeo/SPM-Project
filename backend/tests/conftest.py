import pytest
import os
from supabase import create_client, Client
import json
import sys
sys.path.append("./backend/")
from flaskapp.__init__ import create_app

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