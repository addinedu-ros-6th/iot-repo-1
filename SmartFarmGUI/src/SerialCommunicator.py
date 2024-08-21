import serial
import struct
import time
from PyQt5.QtCore import *


class Connector:
  def __init__(self):
    self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    self.uid = bytes(4)
    return

  def send(self, command, data=0):
    req_data = struct.pack('<2sic', command, data, b'\n')
    self.conn.write(req_data)
    return
    
  def __del__(self):
    print("__del__")
    self.conn.close()


class Sender(QThread):
  update = pyqtSignal()

  def __init__(self, sec, signal):
    super().__init__()
    self.sec = sec
    self.running = True

    self.update.connect(signal)

  def run(self):
    while self.running == True:
      self.update.emit()
      time.sleep(self.sec)

  def stop(self):
    self.running = False


class Receiver(QThread):
  received_env_value = pyqtSignal(tuple)
  received_env_io_result = pyqtSignal(int, bool)
  request_log = pyqtSignal(str, int)

  def __init__(self, conn):
    super().__init__()
    self.is_running = False
    self.conn = conn
    
    print("recv init")

  def run(self):
    self.is_running = True
    while (self.is_running == True):
      if self.conn.readable():
        res = self.conn.read_until(b'\n')
        if len(res) > 0:

          res = res[:-2]
          cmd = res[:2].decode()

          # 환경(온도, 습도, 빛) 수치 응답
          if cmd == 'GE' and res[2] == 0:
            temp = int.from_bytes(res[3:5], 'little')
            humidity = int.from_bytes(res[5:7], 'little')
            light = int.from_bytes(res[7:9], 'little')
            print(f"Aircon: {temp}, Heating: {humidity}, Light: {light}")
            self.received_env_value.emit((temp, humidity, light))

          # 환경 수치 io 실행 응답 
          elif cmd == 'SE' and res[2] == 0:
            value = int.from_bytes(res[3:5], 'little')
            self.received_env_io_result.emit(value, True)
            self.request_log.emit('SE', value)

          # 환경 수치 io 종료 응답
          elif cmd == 'EE' and res[2] == 0:
            value = int.from_bytes(res[3:5], 'little')
            self.received_env_io_result.emit(value, False)
            # print("EE ", value)

          # 마사지 요청에 대한 응답
          elif cmd == "SA" and res[2] == 0:
            print("마사지")

          # 치료 요청 응답
          elif cmd == "ST" and res[2] == 0:
            value = int.from_bytes(res[3:4], 'little')
            print("치료 진행 : ", value)

          else:
            print("unknown error")
            print(res)

  def stop(self):
    print("recv stop")
    self.running = False
