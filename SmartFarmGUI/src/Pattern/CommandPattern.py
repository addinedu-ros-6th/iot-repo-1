from abc import ABC, abstractmethod

class Command(ABC):
  @abstractmethod
  def execute(self):
    pass

class SetEnvironmentCommand(Command):
  def __init__(self, receiver, io_index):
    self.receiver = receiver
    self.io_index = io_index
  
  def execute(self):
    self.receiver.send(b"SE", self.io_index)
    print("SetEnvironmentCommand send: SE", self.io_index)

class EndEnvironmentCommand(Command):
  def __init__(self, receiver, io_index):
    self.receiver = receiver
    self.io_index = io_index
  
  def execute(self):
    self.receiver.send(b"EE", self.io_index)
    print("SetEnvironmentCommand send: EE", self.io_index)