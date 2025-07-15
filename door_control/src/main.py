# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Alfredo Diaz Claro                                                           #
# 	Created:      21/10/2024, 10:55:10 PM                                        #
# 	Description:  EXP project                                                  #
#                                                                              #
# ---------------------------------------------------------------------------- #
#vex:disable=repl

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

# Motor config
brain_inertial = Inertial()
door_motor = Motor(Ports.PORT1)


brain.screen.print("Control de ingreso!")

def serial_monitor():
    try:
        s = open('/dev/serial1','rb')
    except:
        raise Exception('Puerto serial no disponible')
    
    while True:
        data= s.read(1)
        print(data)
        if data == b'a' or data == b'A':
            brain.screen.print_at("Abre puerta", x=5, y=40)
            door_motor.spin_to_position(-90, DEGREES, 25, RPM)
        elif data == b'c' or data == b'C':
            brain.screen.print_at("Cierra puerta", x=5, y=40)
            door_motor.spin_to_position(0, DEGREES, 25, RPM)
            
        
t1=Thread(serial_monitor)


        
