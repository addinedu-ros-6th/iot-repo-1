from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys

import SerialCommunicator as SC 


class SmartFarmManager(QObject):
  env_data_updated = pyqtSignal(list)
  env_io_updated = pyqtSignal(int, bool)

  def __init__(self):
    self.connector = SC.Connector()

    self.sender = SC.Sender(2, self.update_get_env_data)
    self.receiver = SC.Receiver(self.connector.conn)
    self.receiver.received_env_value.connect(self.update_env_cur_value)
    self.receiver.received_env_io_result.connect(self.update_env_io_icon)

  def update_get_env_data(self):
    self.connector.send(b"GE")
    return
  
  # 아두이노에서 온도, 습도 등의 수치를 받으면 UI 텍스트를 변경한다.
  def update_env_cur_value(self, envValues):
    self.env_data_updated.emit(envValues) 
    return
  
  # 아두이노에서 신호를 받으면 io의 아이콘을 활성 / 비활성화한다.
  def update_env_io_icon(self, command, io_index):
    isOn = command == "SE"
    self.env_io_updated.emit(io_index, isOn)
    return