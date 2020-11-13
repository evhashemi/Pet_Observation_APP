import requests
import json

apiKey = '9ad6faa224123062e7975db7b1e63415'

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
