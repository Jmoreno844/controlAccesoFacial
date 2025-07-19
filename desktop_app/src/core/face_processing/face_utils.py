import os
import numpy as np
import cv2
import datetime
from typing import List, Tuple, Any, Optional, Dict
from core.face_processing.models.face_detect_model import FaceDetectMediapipe
from core.face_processing.models.face_mesh_model import FaceMeshMediapipe
from core.face_processing.models.face_matcher_model import FaceMatcherModels
from api.api_client import ApiClient


class FaceUtils:
    def __init__(self, api_client: ApiClient):
        # face detect
        self.face_detector = FaceDetectMediapipe()
        # face mesh
        self.mesh_detector = FaceMeshMediapipe()
        # face matcher
        self.face_matcher = FaceMatcherModels()

        # variables
        self.angle = None
        self.face_db = []
        self.face_names = []
        self.distance: float = 0.0
        self.matching: bool = False
        self.user_registered = False
        
        # API client for logging
        self.api_client = api_client

    # detect
    def check_face(self, face_image: np.ndarray) -> Tuple[bool, Any, np.ndarray]:
        face_save = face_image.copy()
        check_face, face_info = self.face_detector.face_detect_mediapipe(face_image)
        return check_face, face_info, face_save

    def extract_face_bbox(self, face_image: np.ndarray, face_info: Any):
        h_img, w_img, _ = face_image.shape
        bbox = self.face_detector.extract_face_bbox_mediapipe(w_img, h_img, face_info)
        return bbox

    def extract_face_points(self, face_image: np.ndarray, face_info: Any):
        h_img, w_img, _ = face_image.shape
        face_points = self.face_detector.extract_face_points_mediapipe(h_img, w_img, face_info)
        return face_points

    # face mesh
    def face_mesh(self, face_image: np.ndarray) -> Tuple[bool, Any]:
        check_face_mesh, face_mesh_info = self.mesh_detector.face_mesh_mediapipe(face_image)
        return check_face_mesh, face_mesh_info

    def extract_face_mesh(self, face_image: np.ndarray, face_mesh_info: Any) -> List[List[int]]:
        face_mesh_points_list = self.mesh_detector.extract_face_mesh_points(face_image, face_mesh_info, viz=True)
        return face_mesh_points_list

    def check_face_center(self, face_points: List[List[int]]) -> bool:
        check_face_center = self.mesh_detector.check_face_center(face_points)
        return check_face_center

    # crop
    def face_crop(self, face_image: np.ndarray, face_bbox: List[int]) -> np.ndarray:
        h, w, _ = face_image.shape
        offset_x, offset_y = int(w * 0.025), int(h * 0.025)
        xi, yi, xf, yf = face_bbox
        xi, yi, xf, yf = xi - offset_x, yi - (offset_y*4), xf + offset_x, yf
        return face_image[yi:yf, xi:xf]

    # save
    def save_face(self, face_crop: np.ndarray, user_code: str, path: str):
        if len(face_crop) != 0:
            face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f"{path}/{user_code}.png", face_crop)
            return True

        else:
            return False

    # draw
    def show_state_signup(self, face_image: np.ndarray, state: bool, saved: bool = False):
        if saved:
            text = 'Face saved successfully!'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (370, 650 - dim[1]-baseline), (370 + dim[0], 650 + baseline), (0, 0, 0), cv2.FILLED)
            cv2.putText(face_image, text, (370, 650-5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 1)
            self.mesh_detector.config_color((0, 255, 0))
        elif state:
            text = 'Saving face, wait a moment please...'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (370, 650 - dim[1]-baseline), (370 + dim[0], 650 + baseline), (0, 0, 0), cv2.FILLED)
            cv2.putText(face_image, text, (370, 650-5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 1)
            self.mesh_detector.config_color((0, 255, 0))

        else:
            text = 'Face processing, see the camera please!'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (370, 650 - dim[1] - baseline), (370 + dim[0], 650 + baseline), (0, 0, 0),
                          cv2.FILLED)
            cv2.putText(face_image, text, (370, 650 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 0, 0), 1)
            self.mesh_detector.config_color((255, 0, 0))

    def show_state_signup_instructional(self, face_image: np.ndarray):
        """Show instructional state when face is detected but not centered (neutral blue color)."""
        text = 'Please center your face in the camera'
        size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
        dim, baseline = size_text[0], size_text[1]
        cv2.rectangle(face_image, (370, 650 - dim[1] - baseline), (370 + dim[0], 650 + baseline), (0, 0, 0),
                      cv2.FILLED)
        cv2.putText(face_image, text, (370, 650 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 165, 0), 1)  # Orange color
        self.mesh_detector.config_color((255, 165, 0))  # Orange mesh color

    def show_state_login(self, face_image: np.ndarray, state: Optional[bool]):
        if state:
            text = 'Approved face, come in please!'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (370, 650 - dim[1] - baseline), (370 + dim[0], 650 + baseline), (0, 0, 0),
                          cv2.FILLED)
            cv2.putText(face_image, text, (370, 650 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 1)
            self.mesh_detector.config_color((0, 255, 0))

        elif state is None:
            text = 'Comparando rostro, mira la camara Espera 3 segudo por favor!'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (250, 650 - dim[1] - baseline), (250 + dim[0], 650 + baseline), (0, 0, 0),
                          cv2.FILLED)
            cv2.putText(face_image, text, (250, 650 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 0), 1)
            self.mesh_detector.config_color((255, 255, 0))

        elif state is False:
            text = 'Rostro no aprobado, por favor registrarse!'
            size_text = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 1)
            dim, baseline = size_text[0], size_text[1]
            cv2.rectangle(face_image, (370, 650 - dim[1] - baseline), (370 + dim[0], 650 + baseline), (0, 0, 0),
                          cv2.FILLED)
            cv2.putText(face_image, text, (370, 650 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 0, 0), 1)
            self.mesh_detector.config_color((255, 0, 0))

    def read_face_database(self, database_path: Optional[str] = None) -> Tuple[List[np.ndarray], List[str], str]:
        """Read face database from the centralized face_images directory."""
        if database_path is None:
            # Default path to the centralized face_images directory
            # From face_utils.py: go up 4 levels to reach controlAccesoFacial root
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            database_path = os.path.join(base_path, "data", "face_images")
            
        print(f"[DEBUG] Looking for face database at: {database_path}")
        
        self.face_db: List[np.ndarray] = []
        self.face_names: List[str] = []

        if not os.path.exists(database_path):
            print(f"Face database directory not found: {database_path}")
            # Try to create the directory if it doesn't exist
            try:
                os.makedirs(database_path, exist_ok=True)
                print(f"Created face database directory: {database_path}")
            except Exception as e:
                print(f"Failed to create face database directory: {e}")
            return self.face_db, self.face_names, 'No face database found!'

        for file in os.listdir(database_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(database_path, file)
                img_read = cv2.imread(img_path)
                if img_read is not None:
                    self.face_db.append(img_read)
                    self.face_names.append(os.path.splitext(file)[0])

        print(f"[DEBUG] Loaded {len(self.face_db)} faces from database")
        return self.face_db, self.face_names, f'Comparando {len(self.face_db)} rostros!'

    def face_matching(self, current_face: np.ndarray, face_db: List[np.ndarray], name_db: List[str]) -> Tuple[bool, str]:
        user_name: str = ''
        print(f"[DEBUG] face_matching: Starting comparison with {len(face_db)} faces in database")
        print(f"Initial current_face - Shape: {current_face.shape}, Dtype: {current_face.dtype}, Min: {np.min(current_face)}, Max: {np.max(current_face)}")
        current_face = cv2.cvtColor(current_face, cv2.COLOR_RGB2BGR)
        print(f"Converted current_face (to BGR) - Shape: {current_face.shape}, Dtype: {current_face.dtype}, Min: {np.min(current_face)}, Max: {np.max(current_face)}")

        for idx, face_img in enumerate(face_db):
            print(f"Database face_img ({name_db[idx]}) - Shape: {face_img.shape}, Dtype: {face_img.dtype}, Min: {np.min(face_img)}, Max: {np.max(face_img)}")
            self.matching, self.distance = self.face_matcher.face_matching_sface_model(current_face, face_img)
            print(f'validating face with: {name_db[idx]}')
            print(f'matching: {self.matching} distance: {self.distance}')
            if self.matching:
                user_name = name_db[idx]
                print(f"[DEBUG] face_matching: Found match! User: {user_name}")
                return self.matching, user_name
                
        print(f"[DEBUG] face_matching: No matches found, returning 'Rostro no conocido'")
        return False, 'Rostro no conocido'

    def user_check_in(self, user_info, access_granted: bool):
        """Create an access log entry for user check-in."""
        try:
            user_id = None
            details = 'Rostro no conocido'

            if access_granted and isinstance(user_info, str) and user_info.isdigit():
                user_id = int(user_info)
                user_data = self.api_client.get_user_by_id(user_id)
                user_name = user_data.get('name', f'ID {user_id}') if user_data else f'ID {user_id}'
                details = f'Acceso concedido a {user_name}'
            elif isinstance(user_info, str):
                details = user_info  # Handles "Rostro no conocido"
            elif isinstance(user_info, dict):
                # Fallback for other potential data structures
                user_id = user_info.get('id')
                user_name = user_info.get('name', 'Usuario Desconocido')
                if access_granted:
                    details = f'Acceso concedido a {user_name}'
                else:
                    details = f'Acceso denegado a {user_name}'
            
            event_type = 'login_success' if access_granted else 'login_failure'
            
            # Create log entry via API
            log_data = {
                'user_id': user_id,
                'event_type': event_type,
                'details': details
            }
            
            response = self.api_client.create_log(log_data)
            
            if response:
                print(f"Access log created successfully for user ID: {user_id}")
                return True
            else:
                print(f"Failed to create access log for user ID: {user_id}")
                return False
                
        except Exception as e:
            print(f"Error creating access log: {e}")
            # Fallback to console logging if API fails
            now = datetime.datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            status = "concedido" if access_granted else "denegado"
            print(f"Acceso {status} a las {date_time} para usuario: {user_info}")
            return False
                

