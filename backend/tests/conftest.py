import pytest
from flaskapp.main import create_app
from supabase import create_client
pytest_plugins = ['pytest_mock']


@pytest.fixture(scope='module')
def app():
    app = create_app()
    # other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture(scope='module')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

