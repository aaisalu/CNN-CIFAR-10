import time

import requests


# Configuration
url = "http://127.0.0.1:8000/account/login/"
payload = {
    "username": "testuser",
    "password": "testpass",
    "csrfmiddlewaretoken": "",  # You may need to fetch this dynamically
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}


# Function to get CSRF token (if CSRF protection is enabled)
def get_csrf_token(session):
    response = session.get("http://127.0.0.1:8000/account/login/")
    if response.status_code == 200:
        # Extract CSRF token from the response (assuming it's in a form)
        import re

        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if match:
            return match.group(1)
    return None


# Test rate limit
def test_rate_limit():
    session = requests.Session()
    # Fetch CSRF token
    csrf_token = get_csrf_token(session)
    if not csrf_token:
        print("Failed to retrieve CSRF token")
        return

    payload["csrfmiddlewaretoken"] = csrf_token

    # Send 12 POST requests to exceed the 10/m limit
    for i in range(12):
        response = session.post(url, data=payload, headers=headers)
        print(f"Request {i + 1}: Status Code = {response.status_code}")
        if response.status_code == 429:
            print("Rate limit exceeded! Received 429 response.")
            print("Response content:", response.text)
            break
        elif response.status_code == 200:
            print(
                "Request successful (form page returned, possibly invalid credentials)."
            )
        elif response.status_code == 302:
            print("Request redirected (possibly successful login).")
        else:
            print(f"Unexpected status code: {response.status_code}")
        time.sleep(0.1)  # Small delay to avoid overwhelming the server


if __name__ == "__main__":
    print("Testing rate limit for login_view...")
    test_rate_limit()
