import serial
import time
import threading


class SerialCommunication:
    def __init__(self):
        # self.com = serial.Serial("COM3", 9600, write_timeout=10)
        # self.running = True
        # # Inicia un hilo para leer continuamente
        # self.read_thread = threading.Thread(target=self.continuous_read, daemon=True)
        # self.read_thread.start()
        pass

    def sending_data(self, command: str) -> None:
        print(f"DEBUG: Sending command: {command.strip()}")
        # self.com.write(command.encode('ascii'))
        pass

    def activate_rotor(self) -> None:
        # self.sending_data("ACTIVATE\n")
        # # read_debug() ya se ejecuta de forma continua en otro hilo
        pass

    def read_debug(self) -> None:
        # # Leer y mostrar mensajes de debug desde el Arduino una vez
        # while self.com.in_waiting:
        #     debug_line = self.com.readline().decode('utf-8').strip()
        #     if debug_line:
        #         print("arduino:", debug_line)
        pass

    def continuous_read(self) -> None:
        # last_debug_time = time.time()
        # # Lee de forma continua mientras la conexión esté activa
        # while self.running:
        #     self.read_debug()
        #     # Imprime un mensaje cada 1 segundo para confirmar que el hilo sigue activo.
        #     if time.time() - last_debug_time >= 1:
        #         #print("DEBUG: continuous_read thread is running")
        #         last_debug_time = time.time()
        #     time.sleep(0.1)  # pequeña pausa para evitar un uso excesivo de CPU
        pass

    def close(self) -> None:
        # self.running = False
        # self.read_thread.join()
        # self.com.close()
        pass
