from app.app import create_app

def test_hello(client):
    response = client.get("/")
    assert "Hello world" in response.json
