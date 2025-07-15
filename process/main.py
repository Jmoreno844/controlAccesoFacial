import os
import datetime
from tkinter import *
import tkinter as Tk
import imutils
from PIL import Image, ImageTk
import cv2
import traceback

from process.gui.image_paths import ImagePaths
from process.database.config import DataBasePaths
from process.face_processing.face_signup import FaceSignUp
from process.face_processing.face_login import FaceLogIn
from process.com_interface.serial_com import SerialCommunication


class CustomFrame(Tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=Tk.BOTH, expand=True)


class GraphicalUserInterface:
    def __init__(self, root):
        self.main_window = root
        self.main_window.title("faces access control")
        self.main_window.geometry("1280x720")
        self.frame = CustomFrame(self.main_window)

        # config stream
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # signup window
        self.signup_window = None
        self.input_name = None
        self.input_user_code = None
        self.name = None
        self.user_code = None
        self.user_list = None
        # face capture
        self.face_signup_window = None
        self.signup_video = None
        self.user_codes = []
        self.data = []

        # login window
        self.face_login_window = None
        self.login_video = None
        self.login_sent = False  # Agrega una bandera para evitar envíos repetidos

        # modules
        self.images = ImagePaths()
        self.database = DataBasePaths()
        self.face_sign_up = FaceSignUp()
        self.face_login = FaceLogIn()
        self.com = SerialCommunication()

        # process
        self.stop_login = False
        self._last_log = datetime.datetime.min
        self._log_interval = datetime.timedelta(seconds=0.5)
        self.end_state_display_active = False # Flag for active approval/denial display
        self.close_timer_id = None      # ID for the close_login timer
        print(f"[DEBUG {datetime.datetime.now()}] __init__: stop_login={self.stop_login}")
        self.main()

    def trigger_delayed_close(self):
        print(f"[DEBUG {datetime.datetime.now()}] trigger_delayed_close: Timer expired, proceeding to close login.")
        self.end_state_display_active = False
        self.close_timer_id = None
        self.close_login()

    def close_login(self):
        timestamp = datetime.datetime.now()
        print(f"[DEBUG {timestamp}] close_login: ENTRY - Current stop_login = {self.stop_login}")
        try:
            # Cancel any pending close timer if close_login is called directly
            if self.close_timer_id:
                if hasattr(self, 'login_video') and self.login_video and self.login_video.winfo_exists():
                    self.login_video.after_cancel(self.close_timer_id)
                self.close_timer_id = None
            self.end_state_display_active = False # Reset display flag

            self.face_login.__init__()
            print(f"[DEBUG {datetime.datetime.now()}] close_login: Re-initialized face_login")
            
            if hasattr(self, 'face_login_window') and self.face_login_window is not None:
                if self.face_login_window.winfo_exists():
                    print(f"[DEBUG {datetime.datetime.now()}] close_login: Destroying face_login_window")
                    self.face_login_window.destroy()
                else:
                    print(f"[DEBUG {datetime.datetime.now()}] close_login: face_login_window does not exist (winfo_exists=False)")
            else:
                print(f"[DEBUG {datetime.datetime.now()}] close_login: face_login_window is None or not initialized")
            
            if hasattr(self, 'login_video') and self.login_video is not None:
                if self.login_video.winfo_exists():
                    print(f"[DEBUG {datetime.datetime.now()}] close_login: Destroying login_video")
                    self.login_video.destroy()
                else:
                    print(f"[DEBUG {datetime.datetime.now()}] close_login: login_video does not exist (winfo_exists=False)")
            else:
                print(f"[DEBUG {datetime.datetime.now()}] close_login: login_video is None or not initialized")
            
            self.login_sent = False
            self.stop_login = True
            print(f"[DEBUG {datetime.datetime.now()}] close_login: Set stop_login = {self.stop_login}, login_sent = {self.login_sent}")
        except Exception as e:
            print(f"[ERROR {datetime.datetime.now()}] close_login: Exception: {e}")
            print(traceback.format_exc())
        finally:
            print(f"[DEBUG {datetime.datetime.now()}] close_login: EXIT - Final stop_login = {self.stop_login}")

    def facial_login(self):
        now = datetime.datetime.now()
        log_printed_this_cycle = False
        if (now - self._last_log) >= self._log_interval:
            print(f"[DEBUG {now}] facial_login: ENTRY stop_login={self.stop_login}, end_state_active={self.end_state_display_active}")
            log_printed_this_cycle = True
        
        if self.stop_login: # This is the main gatekeeper, set by close_login
            if log_printed_this_cycle: self._last_log = now
            return
        
        # Check if required objects exist
        if not hasattr(self, 'cap') or self.cap is None:
            print(f"[DEBUG {now}] facial_login: Camera (cap) is None or not initialized")
            return
            
        if not hasattr(self, 'login_video') or self.login_video is None:
            print(f"[DEBUG {now}] facial_login: login_video is None or not initialized")
            self.stop_login = True
            print(f"[DEBUG {now}] facial_login: Set stop_login = {self.stop_login} due to missing login_video")
            return
            
        if not self.login_video.winfo_exists():
            print(f"[DEBUG {now}] facial_login: login_video does not exist (winfo_exists=False)")
            self.stop_login = True
            print(f"[DEBUG {now}] facial_login: Set stop_login = {self.stop_login} due to non-existent login_video")
            return
        
        # Read frame from camera
        if not self.cap.isOpened():
            print(f"[DEBUG {now}] facial_login: Camera is not open")
            return
            
        ret, frame_bgr = self.cap.read()
        
        if not ret:
            # schedule next check quickly (e.g. 10ms)
            if self.login_video.winfo_exists():
                self.login_video.after(10, self.facial_login)
            if log_printed_this_cycle : self._last_log = now # Update if we logged ENTRY
            return
        
        # Process the frame
        frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        # Ensure self.face_login.process returns frame, user_access, info
        processed_frame, user_access, info = self.face_login.process(frame) 
        
        if self.login_video.winfo_exists():
            display_frame = imutils.resize(processed_frame, width=1280) 
            im = Image.fromarray(display_frame)
            img = ImageTk.PhotoImage(image=im)
            self.login_video.configure(image=img)
            self.login_video.image = img


        if user_access and not self.login_sent: # Approved state
            if not self.end_state_display_active:
                print(f"[DEBUG {now}] facial_login: User APPROVED. Activating 1s display timer.")
                self.end_state_display_active = True
                self.login_sent = True # Ensure com_data is sent only once
                self.com.sending_data("A")
                if self.close_timer_id: # Cancel any pre-existing timer
                    if hasattr(self, 'login_video') and self.login_video and self.login_video.winfo_exists():
                        self.login_video.after_cancel(self.close_timer_id)
                if self.login_video.winfo_exists():
                    self.close_timer_id = self.login_video.after(1000, self.trigger_delayed_close)

        elif not user_access and isinstance(info, str) and \
             (info == "Rostro no conocido" or "no aprobado" in info.lower()): # Denied state
            if not self.end_state_display_active:
                print(f"[DEBUG {now}] facial_login: DENIED ('{info}'). Activating 1s display timer.")
                self.end_state_display_active = True
                if self.close_timer_id: # Cancel any pre-existing timer
                    if hasattr(self, 'login_video') and self.login_video and self.login_video.winfo_exists():
                         self.login_video.after_cancel(self.close_timer_id)
                
                if self.login_video.winfo_exists():
                    self.close_timer_id = self.login_video.after(1000, self.trigger_delayed_close)
        
        # Continue the loop to display frames, including the 1s approval/denial
        if self.login_video.winfo_exists() and not self.stop_login:
            self.login_video.after(10, self.facial_login)
        elif not self.login_video.winfo_exists():
             print(f"[DEBUG {now}] facial_login: login_video destroyed, stopping loop.")
             self.stop_login = True

        if log_printed_this_cycle:
            print(f"[DEBUG {now}] facial_login: EXIT")
            self._last_log = now

    def gui_login(self):
        timestamp = datetime.datetime.now()
        print(f"[DEBUG {timestamp}] gui_login: ENTRY - Current stop_login = {self.stop_login}, end_state_active={self.end_state_display_active}")
        
        try:
            # Reset flags and timers before starting new login attempt
            self.stop_login = False
            self.login_sent = False
            self.end_state_display_active = False # Reset display flag
            if self.close_timer_id:
                if hasattr(self, 'login_video') and self.login_video and self.login_video.winfo_exists():
                    self.login_video.after_cancel(self.close_timer_id)
                else:
                    print(f"[DEBUG {timestamp}] gui_login: close_timer_id existed but login_video did not. Cannot cancel.")
                self.close_timer_id = None
            
            print(f"[DEBUG {timestamp}] gui_login: Reset flags: stop_login={self.stop_login}, login_sent={self.login_sent}, end_state_active={self.end_state_display_active}")
            
            # Create new login window
            print(f"[DEBUG {timestamp}] gui_login: Creating new face login window")
            self.face_login_window = Toplevel()
            self.face_login_window.title("face login")
            self.face_login_window.geometry("1280x720")
            
            # Create new video display widget
            print(f"[DEBUG {timestamp}] gui_login: Creating login_video widget")
            self.login_video = Label(self.face_login_window)
            self.login_video.place(x=0, y=0)
            
            # Handle window close event
            def on_window_close():
                print(f"[DEBUG {datetime.datetime.now()}] Window close event triggered by user")
                # self.stop_login = True # Ensure immediate stop if user closes
                self.close_login() # Call full cleanup
            
            self.face_login_window.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Start face processing
            print(f"[DEBUG {timestamp}] gui_login: Starting facial_login")
            self.facial_login()
        except Exception as e:
            print(f"[ERROR {timestamp}] gui_login: Exception: {e}")
            print(traceback.format_exc())
        finally:
            print(f"[DEBUG {timestamp}] gui_login: EXIT")

    def close_signup(self):
        self.face_sign_up.__init__()
        self.face_signup_window.destroy()
        self.signup_video.destroy()

    def facial_sign_up(self):
        if self.cap:
            ret, frame_bgr = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # process
                frame, save_image, info = self.face_sign_up.process(
                    frame, self.user_code
                )

                # config video
                frame = imutils.resize(frame, width=1280)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)

                # show frames
                self.signup_video.configure(image=img)
                self.signup_video.image = img
                self.signup_video.after(10, self.facial_sign_up)

                if save_image:
                    self.signup_video.after(3000, self.close_signup)

        else:
            self.cap.release()

    def data_sign_up(self):
        # extract data
        self.name, self.user_code = self.input_name.get(), self.input_user_code.get()
        # check data
        if len(self.name) == 0 or len(self.user_code) == 0:
            print("¡Formularo  incompleto!")
        else:
            # check user
            self.user_list = os.listdir(self.database.check_users)
            for u_list in self.user_list:
                user = u_list
                user = user.split(".")
                self.user_codes.append(user[0])
            if self.user_code in self.user_codes:
                print("¡Previously registered user!")
            else:
                # save data
                self.data.append(self.name)
                self.data.append(self.user_code)

                file = open(f"{self.database.users}/{self.user_code}.txt", "w")
                file.writelines(self.name + ",")
                file.writelines(self.user_code + ",")
                file.close()

                # clear
                self.input_name.delete(0, END)
                self.input_user_code.delete(0, END)

                # face register
                self.face_signup_window = Toplevel()
                self.face_signup_window.title("face capture")
                self.face_signup_window.geometry("1280x720")

                self.signup_video = Label(self.face_signup_window)
                self.signup_video.place(x=0, y=0)
                self.signup_window.destroy()
                self.facial_sign_up()

    def gui_signup(self):
        self.signup_window = Toplevel(self.frame)
        self.signup_window.title("facial sign up")
        self.signup_window.geometry("1280x720")

        # background
        background_signup_img = PhotoImage(file=self.images.gui_signup_img)
        background_signup = Label(self.signup_window, image=background_signup_img)
        background_signup.image = background_signup_img
        background_signup.place(x=0, y=0)

        # input data
        self.input_name = Entry(self.signup_window)
        self.input_name.place(x=585, y=320)
        self.input_user_code = Entry(self.signup_window)
        self.input_user_code.place(x=585, y=475)

        # input button
        register_button_img = PhotoImage(file=self.images.register_img)
        register_button = Button(
            self.signup_window,
            image=register_button_img,
            height="40",
            width="200",
            command=self.data_sign_up,
        )
        register_button.image = register_button_img
        register_button.place(x=1005, y=565)

    def main(self):
        # Load original background image using PIL and store it
        self.background_img_original = Image.open(self.images.init_img)
        initial_img = ImageTk.PhotoImage(self.background_img_original)
        self.background_label = Label(self.frame, image=initial_img, text="back")
        self.background_label.image = initial_img
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        # Bind window resize event to adjust background image
        self.main_window.bind("<Configure>", self.resize_background)

        # buttons
        login_button_img = PhotoImage(file=self.images.login_img)
        login_button = Button(
            self.frame,
            image=login_button_img,
            height="40",
            width="200",
            command=self.gui_login,
        )
        login_button.image = login_button_img
        login_button.place(x=980, y=325)

        signup_button_img = PhotoImage(file=self.images.signup_img)
        signup_button = Button(
            self.frame,
            image=signup_button_img,
            height="40",
            width="200",
            command=self.gui_signup,
        )
        signup_button.image = signup_button_img
        signup_button.place(x=980, y=478)

    def resize_background(self, event):
        # Resize only if triggered by main window changes
        if event.widget == self.main_window:
            new_width, new_height = event.width, event.height
            resized = self.background_img_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(resized)
            self.background_label.configure(image=new_photo)
            self.background_label.image = new_photo
