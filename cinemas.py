from datetime import date

import requests
from requests.exceptions import ConnectionError


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
                'year': movie_info['ProductionYear'],
            }
            for movie_info in afisha_movies_info_page['MovieList']['Items']
        ]

        if page_number >= afisha_movies_info_page['Pager']['PagesCount']:
            break

        page_number = page_number + 1


def main():
    scheduled_date = date.today().strftime('%d-%m-%Y')
    afisha_movies_info = []

    for afisha_movies_info_page in get_afisha_movies_info(scheduled_date):
        afisha_movies_info.extend(afisha_movies_info_page)


if __name__ == '__main__':
    main()
