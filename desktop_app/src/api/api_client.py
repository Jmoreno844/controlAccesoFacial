import requests
import socket
from typing import Optional, Dict, Any

class ApiClient:
    """Handles all communication with the FastAPI backend and a device control server."""
    def __init__(self, main_base_url="http://127.0.0.1:8000/api", device_control_url="http://127.0.0.1:5000"):
        self.main_base_url = main_base_url
        self.device_control_url = device_control_url
        self.session = requests.Session()
        
        # Configure the session with default headers and settings
        self.session.headers.update({
            'User-Agent': 'DesktopApp/1.0',
            'Accept': 'application/json'
        })
        
        # Disable environment-based proxy settings for local communication
        self.session.trust_env = False
        
        print(f"ApiClient initialized for main API: {self.main_base_url}")
        print(f"ApiClient initialized for device control: {self.device_control_url}")
        
        # Test basic connectivity on startup
        self.test_connection()

    def _request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """A centralized method for making API requests."""
        print(f"Making {method} request to: {url}")
        if data:
            print(f"Request data: {data}")
            
        try:
            # Set Content-Type only for requests with a body
            headers = dict(self.session.headers)
            if data:
                headers['Content-Type'] = 'application/json'

            response = self.session.request(method, url, json=data, timeout=10, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                print("Resource not found.")
                return None
                
            response.raise_for_status()
            
            if response.status_code == 204 or not response.content:
                return {}
            
            return response.json()

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error for {method} {url}: {e}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"Timeout error for {method} {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for {method} {url}: {e}")
            return None

    def test_connection(self):
        """Test basic connectivity to both servers."""
        # Test main API server
        print(f"Testing connection to main API root...")
        try:
            response = self.session.get(self.main_base_url.replace('/api', ''), timeout=3)
            print(f"Main API connection test successful. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Main API connection test failed: {e}")
            
        # Test device control server
        print(f"Testing connection to device control server...")
        try:
            response = self.session.get(self.device_control_url, timeout=3)
            print(f"Device control server connection test successful. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Device control server connection test failed: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches a single user by their ID from the main API."""
        url = f"{self.main_base_url}/users/{user_id}"
        return self._request("GET", url)

    def get_user_by_code(self, user_code: str) -> Optional[Dict[str, Any]]:
        """Fetches a single user by their user_code from the main API."""
        url = f"{self.main_base_url}/users/code/{user_code}"
        return self._request("GET", url)

    def create_user(self, name: str, rfid_card_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Creates a new user via the main API."""
        url = f"{self.main_base_url}/users/"
        user_data = {"name": name, "rfid_card_id": rfid_card_id}
        # Filter out None values so the backend receives only provided fields
        user_data = {k: v for k, v in user_data.items() if v is not None and v != ''}
        return self._request("POST", url, data=user_data)

    def create_log(self, log_data: dict) -> Optional[Dict[str, Any]]:
        """Creates a new log entry via the main API."""
        url = f"{self.main_base_url}/logs/"
        return self._request("POST", url, data=log_data)

    def admin_login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Logs in as admin via the main API."""
        url = f"{self.main_base_url}/admin/login"
        print(f"Logging in admin with username: {username}")
        try:
            response = self.session.post(url, data={"username": username, "password": password}, timeout=10)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Admin login failed: {e}")
            return None

    def get_users(self, skip: int = 0, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Fetches a list of all users via the main API."""
        url = f"{self.main_base_url}/users/?skip={skip}&limit={limit}"
        return self._request("GET", url)

    def update_user(self, user_id: int, rfid_card_id: str) -> Optional[Dict[str, Any]]:
        """Updates a user's RFID card via the main API."""
        url = f"{self.main_base_url}/users/{user_id}"
        data = {"rfid_card_id": rfid_card_id}
        return self._request("PUT", url, data=data)

    def get_logs(self, skip: int = 0, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Fetches a list of logs via the main API."""
        url = f"{self.main_base_url}/logs/?skip={skip}&limit={limit}"
        return self._request("GET", url)

    def send_on_signal(self) -> Optional[Dict[str, Any]]:
        """Sends the 'ON' signal to the device control server."""
        url = f"{self.device_control_url}/ON"
        return self._request("GET", url)
