from pydantic import BaseModel
from pathlib import Path


SRC_DIR = Path(__file__).parent.parent.resolve()
ASSETS_DIR = SRC_DIR / "assets" / "ui_images"

class ImagePaths(BaseModel):
    # main images
    init_img: str = str(ASSETS_DIR / 'background.png')
    login_img: str = str(ASSETS_DIR / 'login_button.png')
    signup_img: str = str(ASSETS_DIR / 'signup_button.png')

    # secondary windows
    gui_signup_img: str = str(ASSETS_DIR / 'gui_signup_image.png')
    register_img: str = str(ASSETS_DIR / 'face_capture.png')