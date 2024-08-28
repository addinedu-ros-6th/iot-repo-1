from SerialCommunicator import Connector

class EnvControl():
  def __init__(self, raise_index: int, lower_index: int, connector: Connector):
    self.raise_index = raise_index
    self.lower_index = lower_index
    self.connector = connector

  def raise_control(self):
    self.connector.send(b'SE', self.raise_index)
    if self.raise_index != self.lower_index:
      self.connector.send(b'EE', self.lower_index)

  def lower_control(self):
    self.connector.send(b'EE', self.lower_index)
    if self.raise_index != self.lower_index:
      self.connector.send(b'EE', self.raise_index)

  def maintain_control(self, min_value, max_value, cur_value):
    self.connector.send(b'EE', self.raise_index)
    self.connector.send(b'EE', self.lower_index)
    # recom_value = (min_value + max_value) / 2

    # min_value = recom_value * 0.95
    # max_value = recom_value * 1.05


    # if min_value <= cur_value <= max_value:
    #   self.connector.send(b'EE', self.raise_index)

    #   if self.raise_index != self.lower_index:
    #     self.connector.send(b'EE', self.lower_index)