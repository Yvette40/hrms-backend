import requests

url = "http://127.0.0.1:5000/login"
data = {
    "username": "admin",
    "password": "AdminPass123"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())
