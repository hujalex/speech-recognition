import serial
import time

def send_frustration_value(frustration_value, port='COM5', baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)

        ser.write(str(frustration_value).encode())
        print(f"Sent frustration value: {frustration_value}")
        ser.close()
    except Exception as e:
        print("Error communicating with Arduino:", e)

if __name__ == "__main__":
 
    frustration_value = 2 
    send_frustration_value(frustration_value, port='COM5', baudrate=9600)