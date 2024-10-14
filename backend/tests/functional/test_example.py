

def test_hello(client):
    response = client.get("/")
    assert b"Hello world" in response.data
