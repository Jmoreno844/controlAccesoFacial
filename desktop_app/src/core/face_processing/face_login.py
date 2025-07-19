import numpy as np
from typing import Optional

from core.face_processing.face_utils import FaceUtils


class FaceLogIn:
    def __init__(self, face_utilities: Optional[FaceUtils] = None):
        self.face_utilities = face_utilities if face_utilities else FaceUtils()

        self.matcher = None
        self.comparison = False
        self.cont_frame = 0
        self.processing_state: Optional[bool] = None  # None = processing, True = approved, False = denied

    def process(self, face_image: np.ndarray):
        # step 1: check face detection
        check_face_detect, face_info, face_save = self.face_utilities.check_face(face_image)
        if check_face_detect is False:
            self.processing_state = None
            self.face_utilities.show_state_login(face_image, state=self.processing_state)
            return face_image, self.matcher, '¡ninguna cara fue detectada!'

        # step 2: face mesh
        check_face_mesh, face_mesh_info = self.face_utilities.face_mesh(face_image)
        if check_face_mesh is False:
            self.processing_state = None
            self.face_utilities.show_state_login(face_image, state=self.processing_state)
            return face_image, self.matcher, '¡Ninguna cara mesh detectada!'

        # step 3: extract face mesh
        face_mesh_points_list = self.face_utilities.extract_face_mesh(face_image, face_mesh_info)

        # step 4: check face center
        check_face_center = self.face_utilities.check_face_center(face_mesh_points_list)

        if check_face_center:
            # step 6: extract face info
            # bbox & key_points
            self.cont_frame = self.cont_frame + 1
            print(f"[DEBUG] Face centered, frame count: {self.cont_frame}")
            
            if self.cont_frame >= 48:
                if not self.comparison and self.matcher is None:
                    self.processing_state = None  # Still processing
                    self.face_utilities.show_state_login(face_image, state=self.processing_state)
                    
                    face_bbox = self.face_utilities.extract_face_bbox(face_image, face_info)
                    face_points = self.face_utilities.extract_face_points(face_image, face_info)

                    # step 7: face crop
                    face_crop = self.face_utilities.face_crop(face_save, face_bbox)

                    # Add a sanity check to ensure the crop is not empty
                    if face_crop.size == 0:
                        print("[WARNING] Face crop resulted in an empty image. Skipping frame.")
                        return face_image, self.matcher, 'Error al recortar el rostro'

                    # step 8: read database - use default path (centralized face_images directory)
                    faces_database, names_database, info = self.face_utilities.read_face_database()
                    print(f"[DEBUG] Database loaded: {len(faces_database)} faces")

                    if len(faces_database) != 0:
                        self.comparison = True
                        # step 9: compare faces
                        self.matcher, user_name = self.face_utilities.face_matching(face_crop, faces_database, names_database)
                        print(f"[DEBUG] Face matching result: matcher={self.matcher}, user={user_name}")

                        if self.matcher:
                            # step 10: save data & time - call user_check_in with access granted
                            self.processing_state = True
                            self.face_utilities.show_state_login(face_image, state=self.processing_state)
                            self.face_utilities.user_check_in(user_name, access_granted=True)
                            return face_image, self.matcher, user_name
                        else:
                            # Call user_check_in with access denied for unknown face
                            self.processing_state = False
                            self.face_utilities.show_state_login(face_image, state=self.processing_state)
                            self.face_utilities.user_check_in('Rostro no conocido', access_granted=False)
                            return face_image, self.matcher, 'Rostro no conocido'
                    else:
                        self.processing_state = False
                        self.face_utilities.show_state_login(face_image, state=self.processing_state)
                        return face_image, self.matcher, 'Database vacia'
                else:
                    # Show the current state based on previous matching result
                    self.face_utilities.show_state_login(face_image, state=self.processing_state)
                    if self.matcher:
                        return face_image, self.matcher, 'Aprobado'
                    else:
                        return face_image, self.matcher, 'Rostro no conocido'
            else:
                self.processing_state = None
                self.face_utilities.show_state_login(face_image, state=self.processing_state)
                return face_image, self.matcher, f'Esperando frame de la cara ({self.cont_frame}/48)'
        else:
            # Reset frame counter if face is not centered
            self.cont_frame = 0
            self.processing_state = None
            self.face_utilities.show_state_login(face_image, state=self.processing_state)
            return face_image, self.matcher, 'Cara no está centrada'

