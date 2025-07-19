from ..api.api_client import ApiClient
import datetime

class LogsService:
    def __init__(self):
        self.api_client = ApiClient()

    def create_access_log(self, user_code: str, access_granted: bool, details: str = None):
        """Create an access log entry via the API."""
        try:
            # Get user information by user_code
            user_data = self.api_client.get_user_by_code(user_code) if user_code else None
            
            if user_data:
                user_id = user_data.get('id')
                event_type = 'login_success' if access_granted else 'login_failure'
                if not details:
                    details = 'Acceso concedido' if access_granted else 'Acceso denegado - rostro no reconocido'
            else:
                user_id = None  # For unknown faces
                event_type = 'login_failure'
                if not details:
                    details = 'Rostro no conocido'
            
            # Create log entry via API
            log_data = {
                'user_id': user_id,
                'event_type': event_type,
                'details': details
            }
            
            # Call the logs endpoint
            response = self.api_client.create_log(log_data)
            
            if response:
                print(f"Access log created successfully for user: {user_code}")
                return True
            else:
                print(f"Failed to create access log for user: {user_code}")
                return False
                
        except Exception as e:
            print(f"Error creating access log: {e}")
            # Fallback to console logging if API fails
            now = datetime.datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            status = "concedido" if access_granted else "denegado"
            print(f"Acceso {status} a las {date_time} para usuario: {user_code}")
            return False
