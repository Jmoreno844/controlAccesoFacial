import os
from database.config import DataBasePaths

class UserService:
    def __init__(self):
        self.database = DataBasePaths()

    def check_user_exists(self, user_code):
        user_list = os.listdir(self.database.check_users)
        user_codes = [u.split(".")[0] for u in user_list]
        return user_code in user_codes

    def save_user_data(self, name, user_code):
        try:
            with open(f"{self.database.users}/{user_code}.txt", "w") as file:
                file.writelines(f"{name},{user_code},")
            return True
        except IOError as e:
            print(f"Error saving user data: {e}")
            return False
