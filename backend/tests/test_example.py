from flaskapp.app import createapp

def test_hello(client):
    response = client.get("/")
    assert "Hello world" in response.json
