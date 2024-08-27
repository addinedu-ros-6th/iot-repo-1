from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys
from typing import Type

from Pattern.CommandPattern import SetEnvironmentCommand, EndEnvironmentCommand,Command
import SerialCommunicator as sc

class SmartFarmManager(QObject):

  env_data_updated = pyqtSignal(tuple)

  def __init__(self):
    super().__init__()
    self.connector = sc.Connector()
    self.sc_sender = sc.Sender(2, self.request_get_env_data)
    self.sc_receiver = sc.Receiver(self.connector.conn)
    self.sc_receiver.received_env_value.connect(self.update_env_cur_value)
    

  def __del__(self):
    self.sc_sender.running = False
    self.sc_receiver.running = False


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


  def request_get_env_data(self):
    self.connector.send(b'GE')
    print("request_get_env_data")
    return
  
  def update_env_cur_value(self, env_values):
    print('\033[91m'+'env_values: ' + '\033[92m', str(env_values) +'\033[0m')
    self.env_data_updated.emit(env_values)
    return
  
  def update_env_label_text_color(self, env_data):
    results = []

    for current_value, min_value, max_value, io_indices in env_data:

      if current_value <= min_value:
        color = 'blue'
      elif current_value >= max_value:
        color = 'red'
      else:
        color = 'black'

      for io_index in io_indices:
        self.update_environment_control(color, io_index)
      results.append((current_value, color))

    return results
  
  def update_environment_control(self, color, io_index):
    print(color, io_index)
    device_actions = {
      0: {'red': SetEnvironmentCommand, 'blue': EndEnvironmentCommand, 'black': EndEnvironmentCommand},
      1: {'red': EndEnvironmentCommand, 'blue': SetEnvironmentCommand, 'black': EndEnvironmentCommand},
      2: {'blue': SetEnvironmentCommand, 'black': EndEnvironmentCommand, 'red': EndEnvironmentCommand},
      3: {'red': SetEnvironmentCommand, 'black': EndEnvironmentCommand, 'blue': EndEnvironmentCommand}
    }

    command_class:Type[Command] = device_actions[io_index][color]
    command = command_class(self.connector, io_index)
    command.execute()

  

  
