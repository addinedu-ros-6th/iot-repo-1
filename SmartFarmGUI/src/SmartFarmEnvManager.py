from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys

import SerialCommunicator as SC 


class SmartFarmManager(QObject):
  env_data_updated = pyqtSignal(list)
  env_io_state_updated = pyqtSignal(int, str)
  env_io_state_request = pyqtSignal(str, int)

  def __init__(self):
    self.connector = SC.Connector()

    self.sc_sender = SC.Sender(2, self.request_get_env_data)
    self.receiver = SC.Receiver(self.connector.conn)
    self.receiver.received_env_value.connect(self.update_env_cur_value)
    self.receiver.received_env_io_result.connect(self.update_env_io_icon)

  def __del__(self):
    self.sc_sender.stop()
    self.receiver.stop()

  def send_cmd(self, cmd, data=0):
    cmd = f"{cmd}".encode('utf-8')
    self.connector.send(cmd, data)

  def request_get_env_data(self):
    self.send_cmd("GE")
    return
  
  # 아두이노에서 온도, 습도 등의 수치를 받으면 UI 텍스트를 변경한다.
  def update_env_cur_value(self, envValues):
    self.env_data_updated.emit(envValues) 
    return
  
  # 환경 수치를 표시하는 ui 텍스트 변경
  def update_env_label_text(self, data, env_labels):
    env_labels[0].setText(str(data[0]))
    env_labels[1].setText(str(data[1]))
    env_labels[2].setText(str(data[2]))
    return
  
  # 환경 수치를 표시하는 ui 컬러 변경
  def update_env_label_text_color(self, env_labels, plant_data):
    env_data = [
        (env_labels[0], plant_data.temp_min, plant_data.temp_max, [0, 1]), # 냉방, 난방
        (env_labels[1], plant_data.humidity_min, plant_data.humidity_max, [2]), # 워터펌프
        (env_labels[2], plant_data.light_min, plant_data.light_max, [3]) # 성장 LED
    ]

    for label, min_value, max_value, io_index in env_data:
        cur_value = float(label.text())

        if cur_value < min_value:
            color = "blue"

        elif cur_value > max_value:
            color = "red"
        else:
            color = "black"
        
        label.setStyleSheet(f"color: {color};")
    return

  def update_environment_control(self, color, io_index, io_icons):
    is_icon_visible = io_icons[io_index].isVisible()

    # 이 정보를 DB가 가지고 있으면 더 괜츈할지도?
    device_actions = {
        0: {'red': 'SE', 'blue': 'EE', 'black': 'EE'},  # 에어컨
        1: {'red': 'EE', 'blue': 'SE', 'black': 'EE'},  # 히터
        2: {'blue': 'SE', 'black': 'EE'},               # 가습기
        3: {'red': 'SE', 'black': 'EE'}                 # 조명
    }
    action = device_actions[io_index][color]
    
    if action == 'SE' and not is_icon_visible:
        self.connector.send(b"SE", io_index)
    elif action == 'EE' and is_icon_visible:
        self.connector.send(b"EE", io_index)

  
  # 아두이노에서 신호를 받으면 io의 아이콘을 활성 / 비활성화한다.
  def updated_io_status(self, command, io_index):
    self.env_io_state_updated.emit(io_index, command, io_index)
    return
  
  def update_env_io_icon(self, index, command, io_icon):
    isOn = command == "SE"

    is_io_icon = io_icon.isVisible()
    io_icon.setVisible(isOn)

    return is_io_icon != isOn


    
      