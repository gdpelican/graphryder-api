import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def query_redisgraph(request):
    result = requests.get(user_url, headers={
        'User-Api-Key': config['discourse']['admin_api_key']
    })
    print(result)
    return result
