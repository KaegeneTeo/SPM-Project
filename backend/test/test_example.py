import flask_unittest
import flask.globals
import sys
sys.path.append('./backend/app')
import app

class TestApp(flask_unittest.ClientTestCase):
    app = app
    def test_home(self, client):
        rv = client.get('/')
        self.assertInResponse(rv, 'Hello world!')
