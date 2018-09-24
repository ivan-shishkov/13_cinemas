from datetime import date
import re
import sys

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

        if afisha_movies_info_page is None:
            break

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


def get_top_rated_movies_info(movies_info, movies_count=10):
    return sorted(
        movies_info,
        key=lambda movie: movie.rating if movie.rating else 0,
        reverse=True,
    )[:movies_count]


def print_movies_info(movies_info, title):
    print(title)
    print('{:-<30}'.format(''))

    for movie_number, movie_info in enumerate(movies_info, start=1):
        print('Movie #{}'.format(movie_number))
        print('Title: {}'.format(movie_info.title))
        print('Production year: {}'.format(movie_info.year))
        print('Rating: {}'.format(movie_info.rating))
        print('Votes: {}'.format(movie_info.votes))
        print('{:-<30}'.format(''))


def main():
    scheduled_date = date.today().strftime('%d-%m-%Y')
    movies_info = []

    print('Getting info about movies...')

    for afisha_movies_info_page in get_afisha_movies_info(scheduled_date):
        movies_info.extend(
            get_kinopoisk_movies_info(afisha_movies_info_page)
        )

    if not movies_info:
        sys.exit('Could not get info about movies')

    top_rated_movies_info = get_top_rated_movies_info(movies_info)

    print_movies_info(
        movies_info=top_rated_movies_info,
        title='{} Most Top Rated Movies'.format(len(top_rated_movies_info)),
    )


if __name__ == '__main__':
    main()
