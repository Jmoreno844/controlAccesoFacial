from tkinter import Toplevel, Label, Entry, Button, PhotoImage, END
import cv2
import imutils
from PIL import Image, ImageTk

from ui.image_paths import ImagePaths
from services.user_service import UserService
from core.face_processing.face_signup import FaceSignUp
from core.face_processing.face_utils import FaceUtils

class SignUpWindow:
    def __init__(self, master, face_utils: FaceUtils, cap):
        self.master = master
        self.images = ImagePaths()
        self.user_service = UserService()
        
        # Use the passed-in, pre-loaded instance
        self.face_sign_up = FaceSignUp(face_utils)
        
        self.cap = cap

        self.signup_window = None
        self.input_name = None
        self.input_user_code = None
        self.face_signup_window = None
        self.signup_video = None
        self.user_code = None

        self.show()

    def show(self):
        self.signup_window = Toplevel(self.master)
        self.signup_window.title("facial sign up")
        self.signup_window.geometry("1280x720")

        background_signup_img = PhotoImage(file=self.images.gui_signup_img)
        background_signup = Label(self.signup_window, image=background_signup_img)
        background_signup.image = background_signup_img
        background_signup.place(x=0, y=0)

        self.input_name = Entry(self.signup_window)
        self.input_name.place(x=585, y=320)
        self.input_user_code = Entry(self.signup_window)
        self.input_user_code.place(x=585, y=475)

        register_button_img = PhotoImage(file=self.images.register_img)
        register_button = Button(
            self.signup_window, image=register_button_img, height="40", width="200",
            command=self.data_sign_up,
        )
        register_button.image = register_button_img
        register_button.place(x=1005, y=565)

    def data_sign_up(self):
        name, self.user_code = self.input_name.get(), self.input_user_code.get()
        if not name or not self.user_code:
            print("¡Formulario incompleto!")
            return

        if self.user_service.check_user_exists(self.user_code):
            print("¡Previously registered user!")
        else:
            if self.user_service.save_user_data(name, self.user_code):
                self.input_name.delete(0, END)
                self.input_user_code.delete(0, END)
                self.signup_window.destroy()
                self.start_facial_signup()

    def start_facial_signup(self):
        self.face_signup_window = Toplevel(self.master)
        self.face_signup_window.title("face capture")
        self.face_signup_window.geometry("1280x720")

        self.signup_video = Label(self.face_signup_window)
        self.signup_video.place(x=0, y=0)
        self.facial_sign_up_loop()

    def facial_sign_up_loop(self):
        if self.cap and self.cap.isOpened():
            ret, frame_bgr = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                frame, save_image, info = self.face_sign_up.process(frame, self.user_code)

                frame = imutils.resize(frame, width=1280)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)

                if self.signup_video.winfo_exists():
                    self.signup_video.configure(image=img)
                    self.signup_video.image = img
                    if save_image:
                        self.signup_video.after(3000, self.close_facial_signup)
                    else:
                        self.signup_video.after(10, self.facial_sign_up_loop)
    
    def close_facial_signup(self):
        # Re-initialize the processor state, but not the models
        self.face_sign_up.__init__(self.face_sign_up.face_utilities)
        if self.face_signup_window and self.face_signup_window.winfo_exists():
            self.face_signup_window.destroy()
        
        # Do not release the camera, it's managed by MainWindow
        # if self.cap and self.cap.isOpened():
        #     self.cap.release()
        if self.face_signup_window and self.face_signup_window.winfo_exists():
            self.face_signup_window.destroy()
        if self.cap and self.cap.isOpened():
            self.cap.release()
