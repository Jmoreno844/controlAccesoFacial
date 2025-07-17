from tkinter import Frame, Label, Button, PhotoImage
from PIL import Image, ImageTk
import cv2

from ui.image_paths import ImagePaths
from ui.login_window import LoginWindow
from ui.signup_window import SignUpWindow
from core.face_processing.face_utils import FaceUtils

class MainWindow:
    def __init__(self, root):
        self.main_window = root
        self.main_window.title("faces access control")
        self.main_window.geometry("1280x720")
        
        self.frame = Frame(self.main_window)
        self.frame.pack(fill="both", expand=True)

        self.images = ImagePaths()
        
        # Pre-load models on startup
        print("Pre-loading face processing models...")
        self.face_utils = FaceUtils()
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
        self.background_label.image = initial_img
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_window.bind("<Configure>", self.resize_background)

        login_button_img = PhotoImage(file=self.images.login_img)
        login_button = Button(
            self.frame, image=login_button_img, height="40", width="200",
            command=self.open_login_window
        )
        login_button.image = login_button_img
        login_button.place(x=980, y=325)

        signup_button_img = PhotoImage(file=self.images.signup_img)
        signup_button = Button(
            self.frame, image=signup_button_img, height="40", width="200",
            command=self.open_signup_window
        )
        signup_button.image = signup_button_img
        signup_button.place(x=980, y=478)

    def open_login_window(self):
        LoginWindow(self.main_window, self.face_utils, self.cap)

    def open_signup_window(self):
        SignUpWindow(self.frame, self.face_utils, self.cap)

    def on_closing(self):
        """Handle application closing."""
        print("Releasing camera and closing application...")
        if self.cap.isOpened():
            self.cap.release()
        self.main_window.destroy()

    def resize_background(self, event):
        if event.widget == self.main_window:
            new_width, new_height = event.width, event.height
            resized = self.background_img_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(resized)
            self.background_label.configure(image=new_photo)
            self.background_label.image = new_photo
