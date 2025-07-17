import face_recognition as fr
from deepface import DeepFace
from typing import Tuple
import cv2
import numpy as np


class FaceMatcherModels:
    def __init__(self):
        self.models = [
            "VGG-Face",
            "Facenet",
            "Facenet512",
            "OpenFace",
            "DeepFace",
            "DeepID",
            "ArcFace",
            "Dlib",
            "SFace",
            "GhostFaceNet",
        ]
        print("FaceMatcherModels initialized.")

    def face_matching_face_recognition_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        print("Attempting face matching with face_recognition_model...")
        face_1 = cv2.cvtColor(face_1, cv2.COLOR_BGR2RGB)
        face_2 = cv2.cvtColor(face_2, cv2.COLOR_BGR2RGB)

        face_loc_1 = [(0, face_1.shape[0], face_1.shape[1], 0)]
        face_loc_2 = [(0, face_2.shape[0], face_2.shape[1], 0)]

        face_1_encoding = fr.face_encodings(face_1, known_face_locations=face_loc_1)[0]
        face_2_encoding = fr.face_encodings(face_2, known_face_locations=face_loc_2)

        matching = fr.compare_faces(face_1_encoding, face_2_encoding, tolerance=0.55)
        distance = fr.face_distance(face_1_encoding, face_2_encoding)
        
        print(f"face_recognition_model - Matching: {matching[0]}, Distance: {distance[0]}")
        return matching[0], distance[0]

    def face_matching_vgg_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[0]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_facenet_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[1]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_facenet512_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[2]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_openface_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[3]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_deepface_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[4]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_deepid_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[5]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_arcface_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[6]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_dlib_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[7]
        print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0

    def face_matching_sface_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[8]
        print(f"Attempting face matching with {model_name} model...")
        # log input array details
        print(f"  face_1 -> type: {type(face_1)}, shape: {face_1.shape}, dtype: {face_1.dtype}, min: {np.min(face_1)}, max: {np.max(face_1)}")
        print(f"  face_2 -> type: {type(face_2)}, shape: {face_2.shape}, dtype: {face_2.dtype}, min: {np.min(face_2)}, max: {np.max(face_2)}")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
            print(f"{model_name} - Result: {result}")
            print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model; "
                  f"face_1 shape: {face_1.shape}, face_2 shape: {face_2.shape}, "
                  f"exception: {e}")
            return False, 0.0

    def face_matching_ghostfacenet_model(self, face_1: np.ndarray, face_2: np.ndarray) -> Tuple[bool, float]:
        model_name = self.models[9]
        #print(f"Attempting face matching with {model_name} model...")
        try:
            result = DeepFace.verify(face_1, face_2, model_name=model_name, enforce_detection=False)
            matching, distance = result['verified'], result['distance']
           # print(f"{model_name} - Result: {result}")
            #print(f"{model_name} - Matching: {matching}, Distance: {distance}")
            return matching, distance
        except Exception as e:
            print(f"Error in {model_name} model: {e}")
            return False, 0.0
