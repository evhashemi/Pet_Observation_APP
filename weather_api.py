import requests
import json

apiKey = 'd6efc2f7a9b734a9dbb3463dd5ceeee6'

def make_request():
    param = {
       'access_key' : apiKey,
       'query' : 'Boca Raton'
    }

    weather = requests.get('http://api.weatherstack.com/current?', param)

    if weather.status_code == 200:
        data = weather.json()
        #print(data['current']['pressure'])
        return(data['current']['pressure'])
    else:
        print("error")
        return 0


API = {
    'pressure' : make_request
}

if __name__ == '__main__':
    make_request()
