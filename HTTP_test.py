import requests


def main():
    url = 'http://cit-home1.herokuapp.com/api/register'
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, headers=headers, json={'FirstName': 'Vladislava', 'LastName': 'Kachalova', 'GroupId': 43506})
    print(r.status_code, r.reason)
    print(r.text)
