import pytest
from flaskapp.main import create_app
from supabase import create_client

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

