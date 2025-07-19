import numpy as np
from typing import Tuple, Optional, Any

from api.api_client import ApiClient
from ..face_processing.face_utils import FaceUtils


class FaceSignUp:
    def __init__(self, face_utilities: FaceUtils, face_images_path: Optional[str] = None):
        self.face_utilities = face_utilities
        if face_images_path:
            self.face_images_path = face_images_path
        
        self.face_saved = False
        self.capture_frames = 0

    def reset_state(self):
        """Reset the signup state for a new capture session."""
        self.face_saved = False
        self.capture_frames = 0

    def process(self, face_image: np.ndarray) -> Tuple[np.ndarray, bool, Optional[Any]]:
        # step 1: check face detection
        check_face_detect, face_info, face_save = self.face_utilities.check_face(face_image)
        if check_face_detect is False:
            self.face_utilities.show_state_signup(face_image, state=False, saved=self.face_saved)
            return face_image, False, None

        # step 2: face mesh
        check_face_mesh, face_mesh_info = self.face_utilities.face_mesh(face_image)
        if check_face_mesh is False:
            self.face_utilities.show_state_signup(face_image, state=False, saved=self.face_saved)
            return face_image, False, None

        # step 3: extract face mesh
        face_mesh_points_list = self.face_utilities.extract_face_mesh(face_image, face_mesh_info)

        # step 4: check face center
        check_face_center = self.face_utilities.check_face_center(face_mesh_points_list)

        if check_face_center:
            self.capture_frames += 1
            self.face_utilities.show_state_signup(face_image, state=True, saved=self.face_saved)
            
            if self.capture_frames >= 5 and not self.face_saved:
                face_bbox = self.face_utilities.extract_face_bbox(face_image, face_info)
                face_crop = self.face_utilities.face_crop(face_save, face_bbox)

                # Instead of saving, we now return the cropped face to the UI
                if face_crop.size > 0:
                    self.face_saved = True
                    self.face_utilities.show_state_signup(face_image, state=True, saved=self.face_saved)
                    return face_image, True, face_crop
                else:
                    return face_image, False, None # Crop failed
            else:
                if not self.face_saved:
                    return face_image, False, None
                else:
                    self.face_utilities.show_state_signup(face_image, state=True, saved=self.face_saved)
                    return face_image, True, None
        else:
            self.capture_frames = 0
            if check_face_detect and check_face_mesh:
                self.face_utilities.show_state_signup_instructional(face_image)
                return face_image, False, None
            else:
                self.face_utilities.show_state_signup(face_image, state=False, saved=self.face_saved)
                return face_image, False, None



