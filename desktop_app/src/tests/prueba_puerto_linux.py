import serial

try:
    ser = serial.Serial("/dev/ttyS3", 9600)
    print("Serial port opened successfully!")
    ser.close()
except Exception as e:
    print("Error accessing the serial port:", e)