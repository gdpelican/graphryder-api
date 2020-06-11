import requests
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def query_redisgraph(query):
    response = requests.post(
        f'{config["discourse"]["url"]}/graphryder/query',
        headers={
            'Content-Type': 'application/json',
            'User-Api-Key': config['discourse']['admin_api_key'],
        },
        json={'query': query}
    )
    if response:
        return response.json()['base']
    else:
        return {'error': f'Query failed with code {response.status_code}'}
