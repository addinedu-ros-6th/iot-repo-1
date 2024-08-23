from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys


from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]
class WindowClass(QMainWindow, from_class):
  def __init__(self):
    super().__init__()
    self.setupUi(self)

    self.reset_ui()
    self.login()


  def reset_ui(self):
    self.label_system_message.hide()
    self.label_select.hide()
    return

  def login(self):
    
    pass

  def init_login_ui(self):

    pass

  def init_logout_ui(self):

    pass






if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())