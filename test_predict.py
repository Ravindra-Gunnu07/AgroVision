import requests
import json

# Test the /predict endpoint
url = "http://127.0.0.1:5000/predict"

# Open test image and send to server
with open("test_plant.jpg", "rb") as img_file:
    files = {"image": img_file}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))
