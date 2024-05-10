import requests
from os import environ
from typing import Any


def find_bike_route(start_point: tuple[float, float], end_point: tuple[float, float]) -> dict[str, Any]:
    url = 'https://graphhopper.com/api/1/route'

    payload = {
        'profile': 'bike',
        # "point_hint": "string",
        # "snap_prevention": "string",
        # "curbside": "any",
        'locale': 'en',
        'instructions': True,
        # "elevation": "false",
        # 'details': 'string',   # need to read doc to add details
        # "optimize": "false",
        'calc_points': True,
        # "debug": "false",
        'points_encoded': False,
        # "ch.disable": "false",
        # "heading": "0",
        # "heading_penalty": "120",
        # "pass_through": "false",
        # "algorithm": "round_trip",
        # "round_trip.distance": "10000",
        # "round_trip.seed": "0",
        # "alternative_route.max_paths": "2",
        # "alternative_route.max_weight_factor": "1.4",
        # "alternative_route.max_share_factor": "0.6",
        'points': [
            start_point,
            end_point,
        ],
    }
    api_key = {
        'key': environ.get('GRAPHHOPPER_API_KEY'),
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers, params=api_key)

    match response.status_code:
        case 200: return response.json()
        case 400: raise Exception(f'Request is not valid.')
        case 401: raise Exception(f'Authorization is required.')
        case 429: raise Exception(f'API limit reached.')
        case 500: raise Exception(f'Internal server error. Try again.')
        case _: raise Exception(f'Request failed with status code: {response.status_code}')


def find_closest(coordinates: tuple[float, float], what='supermarkets', limit=10) -> list[Any]:
    api_key = environ.get('TOMTOM_API_KEY')
    # url = f'https://graphhopper.com/api/1/navigator/nearest?point={coordinates[0]},{coordinates[1]}&limit={limit}&key={api_key}&type={what}'
    url = f"https://api.tomtom.com/search/2/search/{what}.json?key={api_key}&lat={coordinates[1]}&lon={coordinates[0]}&limit={limit}"

    
    response = requests.get(url)
    match response.status_code:
        case 200: return response.json()
        case _: raise Exception(f'Something went wrong. {response.status_code}')
