import os
import sys
from tkinter import *
import logging as log
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppresses INFO and WARNING messages
import tensorflow as tf
import tensorflow as tf
print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))
log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from process.main import GraphicalUserInterface

app = GraphicalUserInterface(Tk())
app.frame.mainloop()
