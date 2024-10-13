import unittest
import sys
sys.path.append('./backend/app')
import app

app['TESTING'] = True

class TestApp(unittest.TestCase):
    def test_home(self):
        with app.test_client() as client:
            rv = client.get('/')
            self.assertInResponse(rv, 'Hello world!')

if __name__ == '__main__':
    unittest.main()
