from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys

from DataManager import *


from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]
class WindowClass(QMainWindow, from_class):
  def __init__(self):
    super().__init__()
    self.setupUi(self)
    self.db = DataManager()

    self.label_system_message.hide()
    self.label_select.hide()
    self.btn_harvest.hide()

    self.plant_id = 0
    self.startDate
    
    self.login_activated_ui = (self.btn_info)
    self.logout_activated_ui = (self.label_select)
    self.login()


  def login(self):
    grawing_plant_data = self.db.select_data("plant_data", where='isComplete = 0')
    isGrawing = len(grawing_plant_data) > 0
    self.init_ui(isGrawing)





  def init_ui(self, isGrawing):
    self.btn_info.setVisible(isGrawing == True)
    self.btn_info.setVisible(isGrawing == False)


# 이 부분은 Select Window 에서 처리
  def onClick_select(self):

    self.db.insert_data("plant_data", ("state_date", "plant_type", "isComplete"), ())



if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())