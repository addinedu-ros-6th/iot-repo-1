from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys
import os

from DataManager import *
from SmartFarmManager import SmartFarmManager
from collections import namedtuple


PlantData = namedtuple('PlantData', ['id', 'planted_date', 'plant_type', 'isComplete',
                                     'need_day', 'temp_min', 'temp_max', 'humidity_min', 'humidity_max',
                                     'airflow_min', 'airflow_max', 'light_min', 'light_max'])


from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]
class WindowClass(QMainWindow, from_class):

  def __init__(self):
    super().__init__()
    self.setupUi(self)

    self.env_labels = [self.label_cur_temp, self.label_cur_humidity, self.label_cur_light]
    self.io_icons = [self.on_icon_aircon, self.on_icon_heater, self.on_icon_water, self.on_icon_light]

    self.db = DataManager()
    self.smart_farm_manager = SmartFarmManager()
    self.smart_farm_manager.env_data_updated.connect(self.update_env_labels)
    self.plantData = None
    self.login()


  def login(self):
    self.plantData = self.db.select_data("plant_data pd", 
                                             ("pd.id", 
                                              "pd.start_date", 
                                              "pd.plant_type",
                                              "pd.isComplete",
                                              "pi.need_day", 
                                              "pi.temp_min", 
                                              "pi.temp_max", 
                                              "pi.humidity_min", 
                                              "pi.humidity_max", 
                                              "pi.airflow_min", 
                                              "pi.airflow_max", 
                                              "pi.light_min", 
                                              "pi.light_max"), 
                                             join="INNER JOIN plant_info pi ON pd.plant_type = pi.plant_type",
                                             where="isComplete = 0")[0]
                                                  

    print("login grawing_plant_data: ", self.plantData)
    isGrawing = len(self.plantData) > 0
    self.setup_ui(isGrawing)

    if isGrawing == True:
      self.plantData = PlantData(*(self.plantData))
      print('\033[91m'+'self.plantData: ' + '\033[92m', self.plantData)
      self.smart_farm_manager.start_request_env_data()
      self.smart_farm_manager.start_receive_aduino_data()

    else:
      self.smart_farm_manager.stop_request_env_data()
      self.smart_farm_manager.stop_receive_aduino_data()


  def setup_ui(self, isGrawing):
    self.label_system_message.hide()
    self.label_select.hide()
    self.btn_harvest.hide()
    self.btn_info.setVisible(isGrawing == True)
    self.label_select.setVisible(isGrawing == False)


  def update_env_labels(self, env_values):
    env_data = [
      (env_values[0], self.plantData.temp_min, self.plantData.temp_max, [0, 1]),
      (env_values[1], self.plantData.humidity_min, self.plantData.humidity_max, [2]),
      (env_values[2], self.plantData.light_min, self.plantData.light_max, [3])
    ]
    
    results = self.smart_farm_manager.update_env_label_text_color(env_data)

    for label, (value, color) in zip(self.env_labels, results):
      label.setText(str(value))
      label.setStyleSheet(f"color: {color};")
    return
  

if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())