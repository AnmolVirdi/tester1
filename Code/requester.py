import requests

url = 'http://141.148.197.26:5000/process'
data = {'text': 'https://www.hdfcbank.com'} #TEXT KI JAGAH SEARCH QUERY AEGI
response = requests.post(url, data=data)

if response.status_code == 200:
    print(response.text)
else:
    print('Request failed with status code', response.status_code)
