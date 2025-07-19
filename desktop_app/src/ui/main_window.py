from tkinter import Frame, Label, Button, PhotoImage
from PIL import Image, ImageTk
import cv2
from typing import Optional

from api.api_client import ApiClient
from communication.serial_com import SerialCommunication
from core.face_processing.face_utils import FaceUtils
from ui.image_paths import ImagePaths
from ui.login_window import LoginWindow
from ui.signup_window import SignUpWindow

class MainWindow:
    def __init__(self, window, api_client: ApiClient):
        self.window = window
        self.com = SerialCommunication()
        self.api_client = api_client
        self.face_utils = FaceUtils(api_client=self.api_client)

        self.cap = None
        self._is_camera_active = False
        self.main_window = window
        self.main_window.title("faces access control")
        self.main_window.geometry("1280x720")
        
        # Set up proper window close handling
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.frame = Frame(self.main_window)
        self.frame.pack(fill="both", expand=True)

        self.images = ImagePaths()
        
        # Store image references to prevent garbage collection
        self.login_button_img: Optional[PhotoImage] = None
        self.signup_button_img: Optional[PhotoImage] = None
        self.background_label: Optional[Label] = None
        self.background_img_original: Optional[Image.Image] = None
        self.current_background_img: Optional[ImageTk.PhotoImage] = None
        
        # Pre-load models on startup
        print("Pre-loading face processing models...")
        self.face_utils = FaceUtils(api_client=self.api_client)
        print("Models loaded successfully.")
        
        # Pre-initialize camera
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        print("Camera initialized.")
        
        self.setup_ui()

    def setup_ui(self):
        self.background_img_original = Image.open(self.images.init_img)
        initial_img = ImageTk.PhotoImage(self.background_img_original)
        self.background_label = Label(self.frame, image=initial_img)
        # Store reference to prevent garbage collection
        self.current_background_img = initial_img
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_window.bind("<Configure>", self.resize_background)

        self.login_button_img = PhotoImage(file=self.images.login_img)
        login_button = Button(
            self.frame, image=self.login_button_img, height="40", width="200",
            command=self.open_login_window
        )
        login_button.place(x=980, y=325)

        self.signup_button_img = PhotoImage(file=self.images.signup_img)
        signup_button = Button(
            self.frame, image=self.signup_button_img, height="40", width="200",
            command=self.open_signup_window
        )
        signup_button.place(x=980, y=478)
        
        self.admin_button_img = PhotoImage(file=self.images.admin_img)
        admin_button = Button(
            self.frame, image=self.admin_button_img, height="40", width="200",
            command=self.open_admin_login_window
        )
        admin_button.place(x=980, y=628)

    def open_login_window(self):
        # Check if camera is still available
        if not self.cap or not self.cap.isOpened():
            print("Reinitializing camera...")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 1280)
            self.cap.set(4, 720)
        LoginWindow(self.main_window, self.face_utils, self.api_client, self.cap)

    def open_signup_window(self):
        # Check if camera is still available
        if not self.cap or not self.cap.isOpened():
            print("Reinitializing camera...")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 1280)
            self.cap.set(4, 720)
        SignUpWindow(self.main_window, self.face_utils, self.api_client, self.cap)

    def open_admin_login_window(self):
        # Open the admin login window
        from ui.admin_login_window import AdminLoginWindow
        AdminLoginWindow(self.main_window, self.api_client)

    def on_closing(self):
        """Handle application closing."""
        print("Releasing camera and closing application...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.main_window.destroy()

    def resize_background(self, event):
        if event.widget == self.main_window and self.background_img_original:
            new_width, new_height = event.width, event.height
            resized = self.background_img_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.current_background_img = ImageTk.PhotoImage(resized)
            if self.background_label:
                self.background_label.configure(image=self.current_background_img)
