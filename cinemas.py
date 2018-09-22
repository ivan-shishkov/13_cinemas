from datetime import date
import re

import requests
from requests.exceptions import ConnectionError
from kinopoisk.movie import Movie


def fetch_json_content(url, params=None):
    headers = {
        'Accept': 'application/json',
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        return response.json() if response.ok else None
    except ConnectionError:
        return None


def get_afisha_movies_info(scheduled_date):
    page_number = 1

    while True:
        params = {
            'date': scheduled_date,
            'page': page_number,
        }
        afisha_movies_info_page = fetch_json_content(
            url='https://www.afisha.ru/msk/schedule_cinema/',
            params=params,
        )

        yield [
            {
                'name': movie_info['Name'],
                'year': int(movie_info['ProductionYear']),
            }
            for movie_info in afisha_movies_info_page['MovieList']['Items']
        ]

        if page_number >= afisha_movies_info_page['Pager']['PagesCount']:
            break

        page_number = page_number + 1


def get_normalized_movie_name(movie_name):
    return ' '.join(re.findall(r'\w+', movie_name.lower().replace('ё', 'е')))


def get_kinopoisk_movie_info(afisha_movie_info):
    movies = Movie.objects.search(afisha_movie_info['name'])

    normalized_afisha_movie_name = get_normalized_movie_name(
        afisha_movie_info['name'],
    )
    return [
        movie for movie in movies
        if movie.year == afisha_movie_info['year'] and
        get_normalized_movie_name(movie.title) == normalized_afisha_movie_name
    ]


def get_kinopoisk_movies_info(afisha_movies_info):
    movies_info = []

    for afisha_movie_info in afisha_movies_info:
        movies_info.extend(get_kinopoisk_movie_info(afisha_movie_info))

    return movies_info


def main():
    scheduled_date = date.today().strftime('%d-%m-%Y')
    movies_info = []

    for afisha_movies_info_page in get_afisha_movies_info(scheduled_date):
        movies_info.extend(
            get_kinopoisk_movies_info(afisha_movies_info_page)
        )


if __name__ == '__main__':
    main()
