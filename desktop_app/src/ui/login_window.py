import datetime
import traceback
from tkinter import Toplevel, Label
import cv2
import imutils
from PIL import Image, ImageTk
from typing import Optional

from api.api_client import ApiClient
from communication.serial_com import SerialCommunication
from core.face_processing.face_login import FaceLogIn
from core.face_processing.face_utils import FaceUtils

class LoginWindow:
    def __init__(self, master, face_utils: FaceUtils, api_client: ApiClient, cap):
        self.master = master
        self.face_login_window: Optional[Toplevel] = None
        self.login_video: Optional[Label] = None
        self.stop_login = False
        self.login_sent = False
        self.end_state_display_active = False
        self.close_timer_id = None
        self._last_log = datetime.datetime.min
        self._log_interval = datetime.timedelta(seconds=0.5)
        self.failed_reads = 0
        
        # Store image reference to prevent garbage collection
        self.current_video_img: Optional[ImageTk.PhotoImage] = None

        # Use the passed-in, pre-loaded instance
        self.face_login = FaceLogIn(face_utils)
        self.api_client = api_client
        self.com = SerialCommunication()
        self.cap = cap

        self.show()

    def show(self):
        timestamp = datetime.datetime.now()
        print(f"[DEBUG {timestamp}] gui_login: ENTRY")
        
        try:
            self.stop_login = False
            self.login_sent = False
            self.end_state_display_active = False
            self.failed_reads = 0
            if self.close_timer_id:
                if self.login_video and self.login_video.winfo_exists():
                    self.login_video.after_cancel(self.close_timer_id)
                self.close_timer_id = None
            
            self.face_login_window = Toplevel(self.master)
            self.face_login_window.title("face login")
            self.face_login_window.geometry("1280x720")
            
            self.login_video = Label(self.face_login_window)
            self.login_video.place(x=0, y=0)
            
            self.face_login_window.protocol("WM_DELETE_WINDOW", self.close_login)
            
            self.facial_login()
        except Exception as e:
            print(f"[ERROR {timestamp}] gui_login: Exception: {e}")
            print(traceback.format_exc())

    def facial_login(self):
        now = datetime.datetime.now()
        if (now - self._last_log) >= self._log_interval:
            print(f"[DEBUG {now}] facial_login: ENTRY stop_login={self.stop_login}, end_state_active={self.end_state_display_active}")
            self._last_log = now
        
        if self.stop_login:
            return
        
        if not (self.cap and self.cap.isOpened() and self.login_video and self.login_video.winfo_exists()):
            self.close_login()
            return
            
        ret, frame_bgr = self.cap.read()
        
        if not ret:
            self.failed_reads += 1
            if self.failed_reads > 100:  # Stop after 100 failed reads
                print(f"[ERROR] Failed to read frame from camera after {self.failed_reads} attempts. Closing login window.")
                self.close_login()
                return

            if self.login_video.winfo_exists():
                self.login_video.after(10, self.facial_login)
            return

        self.failed_reads = 0  # Reset counter on a successful read
        frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        processed_frame, user_access, info = self.face_login.process(frame)
        
        if self.login_video.winfo_exists():
            display_frame = imutils.resize(processed_frame, width=1280) 
            im = Image.fromarray(display_frame)
            self.current_video_img = ImageTk.PhotoImage(image=im)
            self.login_video.configure(image=self.current_video_img)

        if user_access and not self.login_sent:
            if not self.end_state_display_active:
                print(f"[DEBUG {now}] facial_login: User APPROVED. Activating 1s display timer.")
                self.end_state_display_active = True
                self.login_sent = True
                
                # Send the 'ON' signal to the device control server first
                print("Sending ON signal to device control server...")
                self.api_client.send_on_signal()

                # Then, call user_check_in to log the event to the main server
                self.face_login.face_utilities.user_check_in(info, access_granted=True)
                
                self.com.sending_data("A")
                if self.close_timer_id and self.login_video.winfo_exists():
                    self.login_video.after_cancel(self.close_timer_id)
                if self.login_video.winfo_exists():
                    self.close_timer_id = self.login_video.after(1000, self.trigger_delayed_close)

        elif not user_access and isinstance(info, str) and (info == "Rostro no conocido" or "no aprobado" in info.lower()):
            if not self.end_state_display_active:
                print(f"[DEBUG {now}] facial_login: DENIED ('{info}'). Activating 1s display timer.")
                self.end_state_display_active = True
                
                # Call user_check_in with access denied
                self.face_login.face_utilities.user_check_in(info, access_granted=False)
                
                if self.close_timer_id and self.login_video.winfo_exists():
                     self.login_video.after_cancel(self.close_timer_id)
                if self.login_video.winfo_exists():
                    self.close_timer_id = self.login_video.after(1000, self.trigger_delayed_close)
        
        if self.login_video.winfo_exists() and not self.stop_login:
            self.login_video.after(10, self.facial_login)

    def trigger_delayed_close(self):
        print(f"[DEBUG {datetime.datetime.now()}] trigger_delayed_close: Timer expired, proceeding to close login.")
        self.end_state_display_active = False
        self.close_timer_id = None
        self.close_login()

    def close_login(self):
        print(f"[DEBUG {datetime.datetime.now()}] close_login: ENTRY")
        self.stop_login = True
        try:
            if self.close_timer_id and self.login_video and self.login_video.winfo_exists():
                self.login_video.after_cancel(self.close_timer_id)
                self.close_timer_id = None
            
            # Re-initialize the processor state, but not the models
            self.face_login.__init__(self.face_login.face_utilities)
            
            if self.face_login_window and self.face_login_window.winfo_exists():
                self.face_login_window.destroy()
            
            # Do not release the camera, it's managed by MainWindow
            # The camera should remain open for reuse by other windows

            self.login_sent = False
        except Exception as e:
            print(f"[ERROR {datetime.datetime.now()}] close_login: Exception: {e}")
            print(traceback.format_exc())
       
