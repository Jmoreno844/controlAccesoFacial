from api.api_client import ApiClient

class UserService:
    def __init__(self):
        self.api_client = ApiClient()

    def check_user_exists(self, user_code):
        """Checks if a user exists via the API."""
        try:
            user = self.api_client.get_user_by_code(user_code)
            return user is not None
        except Exception: # Assuming the client raises an exception for 404
            return False

    def save_user_data(self, name, user_code):
        """Saves new user data via the API."""
        new_user = self.api_client.create_user(name=name, user_code=user_code)
        if new_user:
            print(f"Successfully created user: {new_user['name']}")
            return True
        else:
            print(f"Failed to create user with code: {user_code}")
            return False