import argparse

from flask import current_app
from requests_cache import CachedSession

try:
    _api_key = current_app.config['API_KEY']
    _page_limit = current_app.config['PAGE_LIMIT']
    _cache_limit = current_app.config['CACHE_DEFAULT_TIMEOUT']
except RuntimeError:
    _api_key = '3acf214b'
    _page_limit = 10  # set to False if no limit
    _cache_limit = 86400


def get_omdb_movies(title, page=1):
    if title is None:
        return {
            'Status': 'NoTitle',
            'StatusCode': 200,
            'ErrorMessage': 'No title was set'
        }
    else:
        return _get_all_movies(title, page)


def _set_api_key(key):
    global _api_key
    _api_key = key


def _get_all_movies(title, page):
    if _api_key is None:
        call_result = {
            'Status': 'Error',
            'StatusCode': 500,
            'ErrorMessage': 'OMDB API key not set'
        }
    else:
        # r = requests.get(f'http://www.omdbapi.com/?apikey={_api_key}&s={title}&page={page}')
        session = CachedSession('api_cache', backend='sqlite', expire_after=_cache_limit)
        r = session.get(f'http://www.omdbapi.com/?apikey={_api_key}&s={title}&page={page}')
        session.close()
        if r.status_code != 200:
            call_result = {
                'Status': f'Error: {r.status_code}',
                'StatusCode': 500,
                'ErrorMessage': 'Error getting info from OMDB'
            }
        else:
            call_result = _process(title, page, r.json())

    return call_result


def _process(title, page, search_results):
    if search_results['Response'] == 'True':
        total_results = int(search_results['totalResults'])
        if _page_limit:
            if total_results > _page_limit:
                totalpages = total_results // _page_limit
            else:
                totalpages = 1
        else:
            totalpages = total_results // len(search_results['Search'])
        api_results = {
            'Status': 'OK',
            'StatusCode': 200,
            'Page': f'{page} of {totalpages}',
            'Results': []
        }
        _results = []
        for element in search_results['Search']:
            element_result = _get_movie_info(element['imdbID'])
            if element_result:
                _results.append(element_result)

        _results = sort_elements(_results)
        api_results['Results'] = _results
    else:
        api_results = {
            'Status': 'NoData',
            'StatusCode': 200,
            'ErrorMessage': f'No movies or series found with title "{title}"',
            'Page': '0 of 0',
            'Results': []
        }

    return api_results


def _get_movie_info(imdb_id):
    # r = requests.get(f'http://www.omdbapi.com/?apikey={_api_key}&i={imdb_id}')
    session = CachedSession('api_cache', backend='sqlite', expire_after=_cache_limit)
    r = session.get(f'http://www.omdbapi.com/?apikey={_api_key}&i={imdb_id}')
    session.close()
    if r.status_code != 200:
        result = {
            'Status': f'Error: {r.status_code}',
            'ErrorMessage': f'Error getting info from OMDB for movie {imdb_id}',
        }
    else:
        r = r.json()
        if r['imdbRating'] == 'N/A':
            imdbrating = -1
        else:
            imdbrating = float(r['imdbRating'])
        if r['imdbVotes'] == 'N/A':
            imdbvotes = -1
        else:
            imdbvotes = int(r['imdbVotes'].replace(',', ''))
        result = {
            'Title': r['Title'],
            'Year': r['Year'],
            'Released': r['Released'],
            'Runtime': r['Runtime'],
            'Genre': r['Genre'],
            'Plot': r['Plot'],
            'imdbRating': imdbrating,
            'imdbVotes': imdbvotes
        }
        if r['Type'] == 'movie':
            result['BoxOffice'] = r['BoxOffice']
        elif r['Type'] == 'series':
            result['totalSeasons'] = r['totalSeasons']

    return result


def sort_elements(elements):
    sorted_list = [e for e in elements if 'Status' not in e.keys()]
    sorted_list = sorted(sorted_list, key=lambda k: (-k['imdbRating'], -k['imdbVotes'], k['Title']))
    return sorted_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--title")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--apikey", type=str, default=_api_key)

    args = parser.parse_args()

    arg_title = args.title
    arg_page = args.page
    arg_apikey = args.apikey

    _set_api_key(arg_apikey)

    print(get_omdb_movies(arg_title, page=arg_page))
