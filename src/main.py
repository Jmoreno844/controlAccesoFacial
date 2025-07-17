import os
import traceback
import sys

print("Starting application...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")

try:
    # Suppress TensorFlow INFO and WARNING messages
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    print("Set TensorFlow log level...")
    
    import tkinter as tk
    print("Imported tkinter successfully...")
    
    import logging as log
    print("Imported logging successfully...")
    
    import tensorflow as tf
    print("Imported tensorflow successfully...")
    
    # Preload face processing models
    print("Loading face processing models...")
    from core.face_processing.face_utils import FaceUtils
    
    # Create a global instance that will be shared
    global_face_utils = FaceUtils()
    print("Face processing models loaded successfully...")
    
    print("Attempting to import MainWindow...")
    from ui.main_window import MainWindow
    print("Imported MainWindow successfully...")

    def main():
        """Initializes and runs the application."""
        print("Entering main function...")
        
        # Configure logging
        log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        print("Configured logging...")
        
        try:
            # Check for GPU
            print("Checking for GPU...")
            log.info(f"Num GPUs Available: {len(tf.config.list_physical_devices('GPU'))}")
            
            print("Creating tkinter root...")
            root = tk.Tk()
            print("Created tkinter root successfully...")
            
            print("Creating MainWindow...")
            app = MainWindow(root)
            print("Created MainWindow successfully...")
            
            print("Setting up close protocol...")
            root.protocol("WM_DELETE_WINDOW", app.on_closing)
            
            print("Starting mainloop...")
            root.mainloop()
            
        except Exception as e:
            print(f"Error in main function: {e}")
            print(traceback.format_exc())
            input("Press Enter to exit...")

    if __name__ == "__main__":
        print("Running main...")
        main()
        
except Exception as e:
    print(f"Import or initialization error: {e}")
    print(traceback.format_exc())
    input("Press Enter to exit...")