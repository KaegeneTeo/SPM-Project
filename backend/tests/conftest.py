import pytest
from flaskapp.main import create_app
from supabase import create_client
pytest_plugins = ['pytest_mock']

# Mock the Supabase client
@pytest.fixture(scope='module')
def supabase_mock(mocker):
    # Mock the create_client function and return a mocked instance
    mock_supabase_client = mocker.Mock()
    mocker.patch('supabase.create_client', return_value=mock_supabase_client)
    return mock_supabase_client

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

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://mocked.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "mocked_key")