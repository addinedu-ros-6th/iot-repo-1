from abc import ABC, abstractmethod
from SerialCommunicator import Connector

class EnvControl(ABC):
  @abstractmethod
  def control(self, cmd):
    pass

class TemperatureControl(EnvControl):
  def control(self, color, connector: Connector):

    if color == 'red':
      connector.send(b'SE', 0)
      connector.send(b'EE', 1)
    elif color == 'blue':
      connector.send(b'EE', 0)
      connector.send(b'SE', 1)
    elif color == 'black':
      connector.send(b'EE', 0)
      connector.send(b'EE', 1)

  
      
  
