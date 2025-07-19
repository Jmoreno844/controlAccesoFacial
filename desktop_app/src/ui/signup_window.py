from tkinter import Toplevel, Label, Entry, Button, Frame, font, messagebox
import cv2
import imutils
from PIL import Image, ImageTk
import os
from typing import Optional
import numpy as np

from api.api_client import ApiClient
from core.face_processing.face_signup import FaceSignUp
from core.face_processing.face_utils import FaceUtils

class SignUpWindow:
    def __init__(self, master, face_utils: FaceUtils, api_client: ApiClient, cap):
        self.master = master
        self.api_client = api_client
        self.face_utils = face_utils
        self.cap = cap
        self.face_images_path = "data/face_images"
        self.face_signup = FaceSignUp(self.face_utils)

        self.signup_window = Toplevel(self.master)
        self.signup_window.title("Registro de Nuevo Usuario")
        self.signup_window.geometry("800x600")
        
        BG_COLOR = "#0B2027"
        self.signup_window.configure(bg=BG_COLOR)

        self.face_signup_window: Optional[Toplevel] = None
        self.signup_video: Optional[Label] = None
        self.current_video_img: Optional[ImageTk.PhotoImage] = None
        self.captured_face_crop: Optional[np.ndarray] = None
        
        self.input_name: Optional[Entry] = None
        self.input_rfid: Optional[Entry] = None
        self.registration_in_progress = False

        self.setup_ui()

    def setup_ui(self):
        BG_COLOR, TEXT_COLOR, BUTTON_COLOR, ENTRY_BG_COLOR = "#0B2027", "#F0F0F0", "#FF8C00", "#1C3A45"
        
        center_frame = Frame(self.signup_window, bg=BG_COLOR)
        center_frame.pack(expand=True)

        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        Label(center_frame, text="Crear Nuevo Usuario", fg=TEXT_COLOR, bg=BG_COLOR, font=title_font).pack(pady=(0, 40))

        field_font = font.Font(family="Helvetica", size=12)
        label_font = font.Font(family="Helvetica", size=14)

        name_frame = Frame(center_frame, bg=BG_COLOR)
        name_frame.pack(pady=10, fill='x', padx=50)
        Label(name_frame, text="Nombre:", font=label_font, fg=TEXT_COLOR, bg=BG_COLOR, width=15, anchor='w').pack(side="left")
        self.input_name = Entry(name_frame, font=field_font, width=30, bg=ENTRY_BG_COLOR, fg=TEXT_COLOR, relief="flat", insertbackground=TEXT_COLOR)
        self.input_name.pack(side="left", expand=True, fill='x')

        rfid_frame = Frame(center_frame, bg=BG_COLOR)
        rfid_frame.pack(pady=10, fill='x', padx=50)
        Label(rfid_frame, text="Tarjeta RFID (Opcional):", font=label_font, fg=TEXT_COLOR, bg=BG_COLOR, width=15, anchor='w').pack(side="left")
        self.input_rfid = Entry(rfid_frame, font=field_font, width=30, bg=ENTRY_BG_COLOR, fg=TEXT_COLOR, relief="flat", insertbackground=TEXT_COLOR)
        self.input_rfid.pack(side="left", expand=True, fill='x')

        button_font = font.Font(family="Helvetica", size=14, weight="bold")
        Button(
            center_frame, text="Registrar Usuario", font=button_font, command=self.start_facial_signup,
            bg=BUTTON_COLOR, fg="#FFFFFF", relief="flat", padx=20, pady=10, cursor="hand2"
        ).pack(pady=(40, 20))

    def start_facial_signup(self):
        if not self.input_name or not self.input_rfid:
            messagebox.showerror("Error", "UI components not initialized correctly.")
            return

        self.name_to_register = self.input_name.get()
        self.rfid_to_register = self.input_rfid.get()

        if not self.name_to_register:
            messagebox.showerror("Error de Registro", "El nombre es obligatorio.")
            return

        self.signup_window.withdraw()
        self.face_signup_window = Toplevel(self.master)
        self.face_signup_window.title("Captura de Rostro")
        self.face_signup_window.geometry("1280x720")

        self.signup_video = Label(self.face_signup_window)
        self.signup_video.place(x=0, y=0)
        
        self.video_capture_signup()

    def video_capture_signup(self):
        if not (self.cap and self.cap.isOpened() and self.signup_video and self.signup_video.winfo_exists()):
            return

        ret, frame_bgr = self.cap.read()
        if not ret:
            self.signup_video.after(10, self.video_capture_signup)
            return
            
        frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        processed_frame, _, self.captured_face_crop = self.face_signup.process(frame)

        display_frame = imutils.resize(processed_frame, width=1280)
        im = Image.fromarray(display_frame)
        self.current_video_img = ImageTk.PhotoImage(image=im)
        
        if self.signup_video.winfo_exists():
            self.signup_video.configure(image=self.current_video_img)

        if self.captured_face_crop is not None and not self.registration_in_progress:
            self.registration_in_progress = True
            if self.face_signup_window and self.face_signup_window.winfo_exists():
                self.face_signup_window.destroy()
            self.finalize_registration()
        else:
            if self.signup_video.winfo_exists() and not self.registration_in_progress:
                self.signup_video.after(10, self.video_capture_signup)

    def finalize_registration(self):
        name = self.name_to_register
        rfid = self.rfid_to_register or None

        if self.captured_face_crop is None:
            print("Error: No se ha capturado un rostro.")
            self.close_all_windows()
            return

        new_user = self.api_client.create_user(name=name, rfid_card_id=rfid)
        
        if new_user and 'id' in new_user:
            user_id = new_user['id']
            print(f"Usuario '{name}' creado con ID: {user_id}")
            
            if self.face_utils.save_face(self.captured_face_crop, str(user_id), self.face_images_path):
                print(f"Imagen del rostro guardada como '{user_id}.png'")
                messagebox.showinfo("Registro Exitoso", f"Usuario '{name}' registrado correctamente.")
            else:
                print(f"Error al guardar la imagen del rostro para el ID: {user_id}")
                messagebox.showerror("Error de Registro", "No se pudo guardar la imagen del rostro.")
        else:
            print("Error al crear el usuario en la base de datos.")
            messagebox.showerror("Error de Registro", "No se pudo crear el usuario en la base de datos.")

        self.close_all_windows()

    def close_all_windows(self):
        if self.face_signup_window and self.face_signup_window.winfo_exists():
            self.face_signup_window.destroy()
        if self.signup_window and self.signup_window.winfo_exists():
            self.signup_window.destroy()
