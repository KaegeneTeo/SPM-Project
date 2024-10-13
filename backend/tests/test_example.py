def test_hello(client):
    response = client.get("/")
    assert "Hello world" in response.data
