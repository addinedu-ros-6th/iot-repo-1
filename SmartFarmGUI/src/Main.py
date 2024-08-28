import glob

import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import sys
import os

import SmartFarmMonitor as sf
from DataManager import *
from SmartFarmManager import SmartFarmManager
from QDialogPopup import *
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

    self.system_message_timer = QTimer(self) 
    self.age_timer = QTimer(self)
    self.blink_count = 0
    self.image = None
    self.age = 0
    self.pixmap = QPixmap()

    self.farm_monitor = sf.SmartFarmMonitor(self)
    self.farm_monitor.request_care.connect(self.send_data)
    self.farm_monitor.update_camera.connect(self.update_camera)
    
    self.db = DataManager()
    self.smart_farm_manager = SmartFarmManager()
    self.smart_farm_manager.env_value_updated.connect(self.update_env_labels)
    self.smart_farm_manager.env_io_updated.connect(self.update_env_io_icon)
    self.plantData = None
    self.login()


  def login(self):
    plantData = self.db.select_data("plant_data pd", 
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
                                             where="isComplete = 0")
                                                  
    isGrowing = len(plantData) > 0
    self.setup_ui(isGrowing)

    if isGrowing == True:
      self.plantData = plantData[0]
      self.plantData = PlantData(*(self.plantData))
      self.smart_farm_manager.start_request_env_data()
      self.smart_farm_manager.start_receive_aduino_data()
      self.age_timer.timeout.connect(self.add_age) # 시연을 위한 코드
      self.age_timer.start(1000)


    else:
      self.smart_farm_manager.stop_request_env_data()
      self.smart_farm_manager.stop_receive_aduino_data()
      self.farm_monitor.classification_stop()
      self.farm_monitor.detector_stop()
      self.open_select_window()

  def add_age(self):
    # self.age = (datetime.now() - self.plantData.planted_date).days
    self.age += 1 # 시연을 위한 코드
    if self.age >= self.plantData.need_day:
      self.btn_harvest.show()
      
    self.update_monitoring_thread()
      
  def update_monitoring_thread(self):
    if self.age < 50:

      # classificationThread 시작
      if self.farm_monitor.classificationThread.running == False:
        self.farm_monitor.detector_stop()
        self.farm_monitor.classification_start()

    else:
      # detector 시작
      if self.farm_monitor.detectThread.running == False:
        self.farm_monitor.classification_stop()
        self.farm_monitor.detector_start()


  # select
  def open_select_window(self):
    plant_types = self.db.select_data("plant_info", ("plant_type",))
    select_window = SelectWindow(plant_types)
    select_window.plant_selected.connect(self.on_plant_selected)
    select_window.exec_()

  def on_plant_selected(self, plant_type):
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self.db.insert_data("plant_data", ("start_date", "plant_type", "isComplete"), (today, plant_type, False))

    self.plant_id = self.db.select_last_id("plant_data")
    path = "SmartFarmGUI/record/" +  str(self.plant_id)
    os.mkdir(path)
    self.login()


  def setup_ui(self, isGrawing):
    self.label_system_message.hide()
    self.label_select.hide()
    self.btn_harvest.hide()
    self.btn_info.setVisible(isGrawing == True)
    self.label_select.setVisible(isGrawing == False)


  def update_env_io_icon(self, cmd, io_index):
    isOn = (cmd == 'SE')
    isChange = (isOn != self.io_icons[io_index].isVisible())


    if isChange:
      self.io_icons[io_index].setVisible(isOn)

      if cmd == 'EE':
        if io_index == 0:
          self.insert_log_data("hot")
        elif io_index == 1:
          self.insert_log_data("cold")
        elif io_index == 2:
          self.insert_log_data("thirsty")
        elif io_index == 3:
          self.insert_log_data("dork")
    return
  
  def send_data(self, cmd, data = 0):
    self.smart_farm_manager.send_cmd(cmd, data)
    return

  def update_camera(self, image):
    if image is None:
      return
    
    self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    h, w, c = self.image.shape
    qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

    self.pixmap = self.pixmap.fromImage(qimage)
    self.pixmap = self.pixmap.scaled(self.label_view.width(), self.label_view.height())
    self.label_view.setPixmap(self.pixmap)

  # 환경 수치 관련 라벨의 텍스트 내용과 색깔 변경.
  def update_env_labels(self, env_values):
    env_data = [
      (env_values[0], self.plantData.temp_min, self.plantData.temp_max),
      (env_values[1], self.plantData.humidity_min, self.plantData.humidity_max),
      (env_values[2], self.plantData.light_min, self.plantData.light_max)
    ]
    
    results = self.smart_farm_manager.update_env_label_text_color(env_data)

    for label, (value, color) in zip(self.env_labels, results):
      label.setText(str(value))
      label.setStyleSheet(f"color: {color};")
    return
  

  # log
  def insert_log_data(self, message_type):
    print(message_type)
  
    (message_id, message) = self.db.select_data("message_data", ("id", "message") , f"status = \"{message_type}\"")[0]

    self.set_system_message(message)

    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    path = self.capture()
    self.db.insert_data("log_data", ("plant_id", "plant_age", "message_id", "date", "path"), (self.plantData.id, 0, message_id, today, path))
    return
  
  def set_system_message(self, message):
    self.blink_count = 0
    self.label_system_message.setText(message)
    self.system_message_timer.timeout.connect(self.display_system_message)
    self.system_message_timer.start(500)

  def display_system_message(self):
    self.label_system_message.setVisible(self.blink_count % 2 == 0)
    self.blink_count += 1
    if self.blink_count >=6:
      self.system_message_timer.stop() 
    return

  def onClick_open_logWindow(self):
    log_datas = self.db.select_data(
      table="log_data",
      columns=("log_data.*", "message_data.type", "message_data.message"),
      join="INNER JOIN message_data ON log_data.message_id = message_data.id",
      where=f"log_data.plant_id = {self.plantData.id}"      
    )

    LogWindowClass(log_datas)

  def capture(self, image=None):
    print('\033[91m'+'capture: ' + '\033[92m', "capture")
    if image is None and self.image is None:
      return 
    
    path = os.path.join("SmartFarmGUI", "record", str(self.plantData.id))
    os.makedirs(path, exist_ok=True)
    file_count = len(glob.glob(os.path.join(path, '*')))
    filename = os.path.join(path, f"{file_count}.png")
    
    if image is None:
        image = self.image
    
    cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    return filename if image is None else path

  

if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())