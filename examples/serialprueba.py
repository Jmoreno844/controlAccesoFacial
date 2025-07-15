import serial
import time

class SerialCommunication:
    def __init__(self):
        try:
            self.com = serial.Serial("COM3", A, write_timeout=10)
        except serial.SerialException as e:
            print(f"Error al abrir el puerto: {e}")
            self.com = None

    def sending_data(self, command: str) -> None:
        if self.com is not None:
            self.com.write(command.encode('ascii'))

# Ejemplo de uso
if __name__ == "__main__":
    ser_comm = SerialCommunication()
    if ser_comm.com is not None:
        while True:
            user_input = input("Ingrese 'A' para encender el LED: ")
            ser_comm.sending_data(user_input)
            time.sleep(1)  # Pausa para evitar enviar datos demasiado rápido
    else:
        print("No se pudo establecer la conexión serie.")
