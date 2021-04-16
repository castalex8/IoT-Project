import serial
import serial.tools.list_ports
import logging

logging.getLogger('bridge.microcontroller')


class Microcontroller:
    def __init__(self):
        self.ser = None
        print("Available ports: ")

        ports = serial.tools.list_ports.comports()
        self.final_port_name = None
        for port in ports:
            print(port.device)
            print(port.description)
            if 'arduino' or 'ttyACM' in port.description.lower():
                self.final_port_name = port.device
            print("connecting to " + self.final_port_name)

        try:
            if self.final_port_name is not None:
                self.ser = serial.Serial(self.final_port_name, 9600, timeout=0)
            else:
                print("No locker! Connect a locker microcontroller and restart!")
                logging.critical("No microcontroller not found")
        except:
            print("Error with locker (microcontroller) connection!")
            logging.critical("Error with connection bridge - microcontroller (locker)")

    def send_command(self, command: bytes) -> None:
        try:
            self.ser.write(command)
        except:
            print("No serial port available! Connect a locker microcontroller and restart!")
            logging.critical("No serial port available! microcontroller not found")
