from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys

from DataManager import *
from QtDialogPopup import *
import SmartFarmEnvManager as sfm


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
    self.io_icons = [self.on_icon_aircon, self.on_icon_heater, self.on_icon_water, self.on_icon_light]

    self.login_activated_ui = (self.btn_info)
    self.logout_activated_ui = (self.label_select)
    self.login()

  def login(self):
    grawing_plant_data = self.db.select_data("plant_data", where='isComplete = 0')
    isGrawing = len(grawing_plant_data) > 0
    self.init_ui(isGrawing)

    if isGrawing == True:
      self.farm_manager = sfm.SmartFarmManager()
      self.farm_manager.env_data_updated.connect(self.update_env_labels)
      self.farm_manager.env_io_updated.connect(self.update_env_io_icon)

  def init_ui(self, isGrawing):
    self.btn_info.setVisible(isGrawing == True)
    self.btn_info.setVisible(isGrawing == False)

  def open_selectWindow(self):
    plant_types = self.db.select_data("plant_info", ("plant_type",))
    SelectWindow(plant_types)
    self.login()
  
  def update_env_labels(self, data):
    self.label_cur_temp.setText(str(data[0]))
    self.label_cur_humidity.setText(str(data[1]))
    self.label_cur_light.setText(str(data[2]))
    self.update_env_text_color()
  
  def update_env_io_icon(self, index, isOn):
    self.io_icons[index].setVisible(isOn)

   



if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())