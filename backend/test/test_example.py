import flask_unittest
import flask.globals
import sys
sys.path.append('./backend/app')
import app

class TestApp(flask_unittest.AppTestCase):
    def test_home(self, app):
        with app.test_client() as client:
            rv = client.get('/')
            self.assertInResponse(rv, 'Hello world!')
