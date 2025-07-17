from pydantic import BaseModel

class ImagePaths(BaseModel):
    # main images
    init_img: str = 'src/assets/ui_images/background.png'
    login_img: str = 'src/assets/ui_images/login_button.png'
    signup_img: str = 'src/assets/ui_images/signup_button.png'

    # secondary windows
    gui_signup_img: str = 'src/assets/ui_images/gui_signup_image.png'
    register_img: str = 'src/assets/ui_images/face_capture.png'
