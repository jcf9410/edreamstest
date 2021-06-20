import json
import unittest

import requests

from app import create_app


class FlaskModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_api_key(self):
        try:
            api_key = self.app.config['API_KEY']
        except KeyError:
            api_key = None
        self.assertFalse(api_key is None)
        self.assertTrue(api_key is not None)

    def test_omdbapi(self):
        api_key = self.app.config['API_KEY']
        r = requests.get(f'http://www.omdbapi.com/?apikey={api_key}&i=tt0214341')
        self.assertTrue(r.status_code == 200)
        self.assertFalse(r.status_code != 200)

        response = r.json()

        title = response['Title']
        year = response['Year']
        released = response['Released']
        apiresponse = response['Response']

        self.assertEqual(title, 'Dragon Ball Z')
        self.assertEqual(year, '1996–2003')
        self.assertEqual(released, '13 Sep 1996')
        self.assertEqual(apiresponse, 'True')

    def test_api_flask(self):
        res = self.client.get('/')
        self._test_api_notitle_response(res, mode='flask')

        res = self.client.get('/Fast')
        self._test_api_response_full_ok(res, mode='flask')

        res = self.client.get('/Fast?page=2')
        self._test_api_response_full_ok(res, page=2, mode='flask')

        res = self.client.get('/Fast/3')
        self._test_api_response_full_ok(res, page=3, mode='flask')

        res = self.client.get('/Avengers: Endgame')
        self._test_api_response_partial_ok(res, mode='flask')

        res = self.client.get('/jndfkejiesuejn')
        self._test_api_response_noresults(res, mode='flask')

    def test_api_module(self):
        import app.api.omdbapi as api

        res = api.get_omdb_movies(None)
        self._test_api_notitle_response(res, mode='module')

        res = api.get_omdb_movies('Fast')
        self._test_api_response_full_ok(res, mode='module')

        res = api.get_omdb_movies('Fast', page=2)
        self._test_api_response_full_ok(res, page=2, mode='module')

        res = api.get_omdb_movies('Avengers: Endgame')
        self._test_api_response_partial_ok(res, mode='module')

        res = api.get_omdb_movies('jndfkejiesuejn')
        self._test_api_response_noresults(res, mode='module')

    def _test_api_notitle_response(self, res, mode=None):
        if mode == 'flask':
            status_code = res.status_code
            res = json.loads(res.data)
        elif mode == 'module':
            status_code = res['StatusCode']
        else:
            raise Exception('Unknown mode to test')

        self.assertEqual(200, status_code)
        self.assertEqual('NoTitle', res['Status'])

    def _test_api_response_full_ok(self, res, page=1, mode=None):
        if mode == 'flask':
            status_code = res.status_code
            #print(res.data)
            res_json = json.loads(res.data)
        elif mode == 'module':
            status_code = res['StatusCode']
            res_json = res
        else:
            raise Exception('Unknown mode to test')

        self.assertEqual(200, status_code)
        self.assertEqual('OK', res_json['Status'])
        self.assertEqual(f'{page} of 74', res_json['Page'])
        self.assertEqual(10, len(res_json['Results']))

        ratings = [e['imdbRating'] for e in res_json['Results']]

        _ratings_sorted = ratings[:]
        _ratings_sorted.sort(reverse=True)
        self.assertEqual(ratings, _ratings_sorted)

    def _test_api_response_partial_ok(self, res, mode=None):
        if mode == 'flask':
            status_code = res.status_code
            res_json = json.loads(res.data)
        elif mode == 'module':
            status_code = res['StatusCode']
            res_json = res
        else:
            raise Exception('Unknown mode to test')
        self.assertEqual(200, status_code)
        self.assertEqual('OK', res_json['Status'])
        self.assertEqual('1 of 1', res_json['Page'])
        self.assertEqual(4, len(res_json['Results']))
        self.assertEqual(-1, res_json['Results'][-1]['imdbRating'])

    def _test_api_response_noresults(self, res, mode=None):
        if mode == 'flask':
            status_code = res.status_code
            res_json = json.loads(res.data)
        elif mode == 'module':
            status_code = res['StatusCode']
            res_json = res
        else:
            raise Exception('Unknown mode to test')
        self.assertEqual(200, status_code)
        self.assertEqual('NoData', res_json['Status'])
        self.assertEqual('0 of 0', res_json['Page'])
        self.assertEqual(0, len(res_json['Results']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
