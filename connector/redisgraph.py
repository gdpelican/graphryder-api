import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def query_redisgraph(query):
    result = requests.get(
        f'{config['discourse']['url']}/graphryder/query',
        headers={
            'Content-Type': 'application/json',
            'User-Api-Key': config['discourse']['admin_api_key'],
        },
        body={'query': query}
    )
    print(result)
    return result
