import requests
import json
import socket
import urllib3
import os
import sys
from datetime import datetime
from tkinter import Tk
from unittest.mock import MagicMock

# Mock the missing modules if they are not essential for the test script
try:
    from ui.main_window import MainWindow
    from api.api_client import ApiClient
except ImportError:
    print("Could not import MainWindow or ApiClient. Using mock objects.")
    MainWindow = MagicMock()

class ApiTester:
    """A CLI tool for manually testing API endpoints."""
    def __init__(self):
        self.session = requests.Session()
        self.base_url = ""
        self.proxies = {"http": "", "https": ""}

    def get_server_details(self):
        """Prompt user for server IP and port."""
        ip = input("Enter server IP (default: 127.0.0.1): ").strip() or "127.0.0.1"
        port = input("Enter server port (default: 8000): ").strip() or "8000"
        self.base_url = f"http://{ip}:{port}/api"
        print(f"API base URL set to: {self.base_url}")
        
        # Optionally, configure proxies here if needed
        # proxy_url = "http://user:pass@host:port"
        # self.proxies = {"http": proxy_url, "https": proxy_url}
        
        return self.test_connection()

    def test_connection(self):
        """Test the connection to the configured server."""
        if not self.base_url:
            print("Base URL is not set. Please configure it first.")
            return False

        print(f"\n=== Testing Connection to {self.base_url} ===")
        
        # First, test if the port is open
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.base_url.split(':')[1].split('/')[0], int(self.base_url.split(':')[2])))
            sock.close()
            
            if result == 0:
                print(f"✓ Port {self.base_url.split(':')[2]} is open on {self.base_url.split(':')[1].split('/')[0]}")
            else:
                print(f"✗ Port {self.base_url.split(':')[2]} is closed or not responding on {self.base_url.split(':')[1].split('/')[0]} (error code: {result})")
                return False
        except Exception as e:
            print(f"✗ Socket test failed: {e}")
            return False

        # Test HTTP connection
        try:
            self.session.headers.update({
                'User-Agent': 'ApiTester/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            
            # Use proxies if a proxy URL is set, otherwise use an empty dict
            self.session.proxies.update(self.proxies)
            self.session.trust_env = False

            response = self.session.get(self.base_url.replace('/api', '/docs'), timeout=5)
            response.raise_for_status() 
            print("✓ Connection successful!")
            
            return True
            
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection error: {e}")
            return False
        except requests.exceptions.Timeout as e:
            print(f"✗ Timeout error: {e}")
            return False
        except Exception as e:
            print(f"✗ Other error: {e}")
            return False

    def show_menu(self):
        """Display the main menu."""
        print("\n=== API Test Menu ===")
        print("1. Test GET user by code")
        print("2. Test CREATE user")
        print("3. Test CREATE log")
        print("4. Test custom endpoint")
        print("5. Test connection only")
        print("6. Change server IP/port")
        print("7. Exit")
        print("=" * 20)

    def test_get_user(self):
        """Test GET user by code endpoint."""
        user_code = input("Enter user code to search: ").strip()
        if not user_code:
            print("User code cannot be empty")
            return
        
        url = f"{self.base_url}/users/code/{user_code}"
        print(f"\nTesting GET: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✓ User found:")
                print(json.dumps(response.json(), indent=2))
            elif response.status_code == 404:
                print("✗ User not found")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

    def test_create_user(self):
        """Test CREATE user endpoint."""
        name = input("Enter user name: ").strip()
        user_code = input("Enter user code: ").strip()
        
        if not name or not user_code:
            print("Name and user code cannot be empty")
            return
        
        user_data = {"name": name, "user_code": user_code}
        url = f"{self.base_url}/users/"
        print(f"\nTesting POST: {url}")
        print(f"Data: {json.dumps(user_data, indent=2)}")
        
        try:
            response = self.session.post(url, json=user_data, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code in [200, 201]:
                print("✓ User created successfully:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

    def test_create_log(self):
        """Test CREATE log endpoint."""
        print("\n=== Log Entry Data ===")
        user_code = input("Enter user code: ").strip()
        action = input("Enter action (entry/exit): ").strip()
        location = input("Enter location: ").strip()
        
        if not user_code or not action:
            print("User code and action cannot be empty")
            return
        
        log_data = {
            "user_code": user_code,
            "action": action,
            "location": location or "Unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        url = f"{self.base_url}/logs/"
        print(f"\nTesting POST: {url}")
        print(f"Data: {json.dumps(log_data, indent=2)}")
        
        try:
            response = self.session.post(url, json=log_data, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code in [200, 201]:
                print("✓ Log created successfully:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

    def test_custom_endpoint(self):
        """Test custom endpoint with custom JSON content."""
        print("\n=== Custom Endpoint Test ===")
        
        # Get HTTP method
        print("Available methods: GET, POST, PUT, DELETE, PATCH")
        method = input("Enter HTTP method (default GET): ").strip().upper()
        if not method:
            method = "GET"
        
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            print("Invalid HTTP method. Using GET.")
            method = "GET"
        
        # Get endpoint path
        endpoint = input("Enter endpoint path (e.g., /users/123, /logs): ").strip()
        if not endpoint:
            print("Endpoint path cannot be empty")
            return
        
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        
        # Get JSON content (optional)
        json_data = None
        if method in ["POST", "PUT", "PATCH"]:
            print("\nEnter JSON content (press Enter to skip):")
            print("Example: {\"name\": \"John\", \"age\": 30}")
            json_input = input("JSON: ").strip()
            
            if json_input:
                try:
                    json_data = json.loads(json_input)
                    print(f"✓ JSON parsed successfully: {json.dumps(json_data, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"✗ Invalid JSON format: {e}")
                    return
        
        # Construct full URL
        url = f"{self.base_url}{endpoint}"
        print(f"\nTesting {method}: {url}")
        
        if json_data:
            print(f"Data: {json.dumps(json_data, indent=2)}")
        
        try:
            # Make the request based on method
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=json_data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=json_data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
            elif method == "PATCH":
                response = self.session.patch(url, json=json_data, timeout=10)
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            # Try to parse response as JSON
            try:
                response_json = response.json()
                print("✓ Response JSON:")
                print(json.dumps(response_json, indent=2))
            except json.JSONDecodeError:
                print("Response (text):")
                print(response.text)
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

    def run(self):
        """Main application loop."""
        print("🚀 API Testing Tool")
        print("=" * 50)
        
        # Get initial server configuration
        self.get_server_details()
        
        # Main menu loop
        while True:
            self.show_menu()
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                self.test_get_user()
            elif choice == "2":
                self.test_create_user()
            elif choice == "3":
                self.test_create_log()
            elif choice == "4":
                self.test_custom_endpoint()
            elif choice == "5":
                self.test_connection()
            elif choice == "6":
                self.get_server_details()
                if not self.test_connection():
                    print("❌ Failed to connect to new server.")
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def run_gui_test():
    """Function to run the GUI for manual testing."""
    root = Tk()
    api_client = ApiClient()
    app = MainWindow(root, api_client)
    root.mainloop()

if __name__ == "__main__":
    # To run the GUI for manual inspection, uncomment the following line:
    # run_gui_test()
    tester = ApiTester()
    try:
        tester.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        # Cleanup will happen automatically via __del__
        pass
