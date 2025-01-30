import requests

def authenticate_user(user_id, password):  # Two arguments now
    url = "https://dev-56640944.okta.com"
    payload = {"user_id": user_id, "password": password}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return "Authenticated"
    return "Authentication Failed"