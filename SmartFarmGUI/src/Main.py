from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from collections import namedtuple
import sys

from DataManager import *
from QtDialogPopup import *
import SmartFarmEnvManager as sfm

PlantData = namedtuple('PlantData', ['id', 'planted_date', 'plant_type', 'isComplete'
                                     'need_day', 'temp_min', 'temp_max', 'humidity_min', 'humidity_max',
                                     'airflow_min', 'airflow_max', 'light_min', 'light_max'])

from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]
class WindowClass(QMainWindow, from_class):
  def __init__(self):
    super().__init__()
    self.setupUi(self)
    self.db = DataManager()

    self.plantData = None
    self.age =0

    self.label_system_message.hide()
    self.label_select.hide()
    self.btn_harvest.hide()

    self.io_icons = [self.on_icon_aircon, self.on_icon_heater, self.on_icon_water, self.on_icon_light]
    self.env_labels = [self.label_cur_temp, self.label_cur_humidity, self.label_cur_light]
    self.image = None

    self.login_activated_ui = (self.btn_info)
    self.logout_activated_ui = (self.label_select)
    self.login()

  def login(self):
    grawing_plant_data = self.db.select_data("plant_data", ("*"),
                                             "INNER JOIN plant_info_data ON plant_data.plant_type = plant_info_data.plant_type",
                                             "plant_data.isComplete = 0")
    isGrawing = len(grawing_plant_data) > 0
    self.init_ui(isGrawing)

    if isGrawing == True:
      self.plantData = PlantData(*grawing_plant_data[0])
      self.age = (datetime.now() - self.plantData.planted_date).days

      self.farm_manager = sfm.SmartFarmManager()
      self.farm_manager.env_data_updated.connect(self.update_env_labels)
      self.farm_manager.env_io_state_updated.connect(self.updated_io_state)
      self.farm_manager.env_io_state_request.connect(self.request_env_io_state)

  def init_ui(self, isGrawing):
    self.btn_info.setVisible(isGrawing == True)
    self.btn_info.setVisible(isGrawing == False)

  def open_selectWindow(self):
    # plant_types = self.db.select_data("plant_info", ("plant_type",))
    SelectWindow(self.plantData.plant_type)
    self.login()
 
  def update_env_labels(self, data):
    self.farm_manager.update_env_label_text(data, self.env_labels)
    self.farm_manager.update_env_label_text_color(self.env_labels, self.plantData)
    return

  def request_env_io_state(self, text_color, io_index):
    self.farm_manager.update_environment_control(text_color, io_index, self.io_icons)
    return

  def updated_io_state(self, command, io_index):
    isChanged = self.farm_manager.update_env_io_icon(io_index, command, self.io_icons[io_index])
    if isChanged:
      self.insert_log_data(command, io_index)


  def insert_log_data(self, cmd_type, cmd_value):
    message_type = cmd_type + str(cmd_value)
    message_id = self.db.select_data("message_data", ("id") , f"type = {message_type}")
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    path = self.capture()
    self.db.insert_data("log_data", ("plant_id", "plant_age", "message_id", "date", "path"), (self.plantData.id, self.age, message_id, today,path))
    return
  

  def capture(self):
    path = os.path.join("SmartFarmGUI", "record", str(self.plantData.id))
    os.makedirs(path, exist_ok=True)
    file_count = len(glob.glob(os.path.join(path, '*')))
    filename = path+str(file_count) + '.png'
    cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
    return path


if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())