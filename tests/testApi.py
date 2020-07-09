import unittest
import requests
class TestApi(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testApi(self):
        url ="http://127.0.0.1:5177/api/flats"
        response = requests.get(url)

        print(response.content)