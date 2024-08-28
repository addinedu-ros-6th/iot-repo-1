from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys
from typing import List, Type

from EnvControl import *
import SerialCommunicator as sc


class SmartFarmManager(QObject):

  env_value_updated = pyqtSignal(tuple)
  env_io_updated = pyqtSignal(str, int)
  log_insert = pyqtSignal(str)

  def __init__(self):
    super().__init__()
    self.connector = sc.Connector()
    self.sc_sender = sc.Sender(2, self.request_get_env_data)
    self.sc_receiver = sc.Receiver(self.connector.conn)
    self.sc_receiver.received_env_value.connect(self.update_env_cur_value)
    self.sc_receiver.received_env_io_result.connect(self.update_env_io)
    self.sc_receiver.request_log.connect(self.insert_log_data)

    self.envControls: List[EnvControl] = [
      EnvControl(raise_index=0, lower_index=1, connector= self.connector),  # Temperature
      EnvControl(raise_index=2, lower_index=2, connector= self.connector),  # Humidity
      EnvControl(raise_index=3, lower_index=3, connector= self.connector)   # Light
    ]


  def __del__(self):
    self.sc_sender.running = False
    self.sc_receiver.running = False

  def insert_log_data(self, cmd, data):
    if cmd =='ST':
      msg = None
      if data == 2:
        self.log_insert.emit('yellow')
        pass

  def send_cmd(self, cmd, data=0):
    cmd = f"{cmd}".encode('utf-8')
    self.connector.send(cmd, data)


  def start_request_env_data(self):
    self.sc_sender.running = True
    self.sc_sender.start()
    return

  def stop_request_env_data(self):
    self.sc_sender.running = False
    return
  
  def start_receive_aduino_data(self):
    self.sc_receiver.running = True
    self.sc_receiver.start()
    return
  
  def stop_receive_aduino_data(self):
    self.sc_receiver.running = False
    return

  # 현재 환경 수치를 달라고 요청한다.
  def request_get_env_data(self):
    self.connector.send(b'GE')
    print("request_get_env_data")
    return
  
  # 환경 제어 io의 on/off 상태가 매개변수로 전달된다.
  def update_env_io(self, io_index, cmd):
    self.env_io_updated.emit(cmd, io_index)
    return
  

  # 환경 수치 변화에 따른 라벨 텍스트 변경. (텍스트 내용, 색깔)
  def update_env_cur_value(self, env_values):
    print('\033[91m'+'env_values: ' + '\033[92m', str(env_values) +'\033[0m')
    self.env_value_updated.emit(env_values)
    return
  
  def update_env_label_text_color(self, env_data):
    results = []

    for index, (current_value, min_value, max_value) in enumerate(env_data):

      if current_value <= min_value:
        color = 'blue'
        self.envControls[index].raise_control()
        
      elif current_value >= max_value:
        color = 'red'
        self.envControls[index].lower_control()

      else:
        color = 'black'
        self.envControls[index].maintain_control( current_value)
      
      results.append((current_value, color))

    return results
  
    


  

  
