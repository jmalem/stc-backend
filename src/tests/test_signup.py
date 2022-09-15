import unittest
import requests
from src.service import signup


class MyTestCase(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"

    def test_index(self):
        URL = self.BASE_URL + '/signup'
        data = {
            "username": "aw",
            "password": "123456789"
        }
        response = requests.post(URL, json=data)
        status_code = response.status_code
        self.assertEqual(200, status_code)  # add assertion here
        print(response)

        # test_client = signup.test_client(self)
        # URL = self.BASE_URL + '/signup'
        # data = {
        #     "username": "aw",
        #     "password": "123456789"
        # }
        # response = test_client.post("/signup", json=data)
        # print(response.data)
        # status_code = response.status_code
        # self.assertEqual(200, status_code)  # add assertion here
        # print(response)


if __name__ == '__main__':
    unittest.main()
