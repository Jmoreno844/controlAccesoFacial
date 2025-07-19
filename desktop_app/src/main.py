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
    
    # Conditional imports for application components
    try:
        from ui.main_window import MainWindow
        from api.api_client import ApiClient
        print("Imported MainWindow successfully...")
    except ImportError as e:
        print(f"UI or API component import error: {e}")
        # Handle error appropriately, maybe exit

    def main():
        """Main function to initialize and run the application."""
        print("Starting application...")
        root = tk.Tk()
        
        # Create a single ApiClient instance
        api_client = ApiClient()
        
        # Pass the api_client to the MainWindow
        app = MainWindow(root, api_client)
        
        root.mainloop()
        print("Application finished.")

    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Import or initialization error: {e}")
    print(traceback.format_exc())
    input("Press Enter to exit...")