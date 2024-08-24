from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from collections import namedtuple
import sys

from DataManager import *
from QtDialogPopup import *
import SmartFarmEnvManager as sfm
import pygame

PlantData = namedtuple('PlantData', ['id', 'planted_date', 'plant_type', 'isComplete',
                                     'need_day', 'temp_min', 'temp_max', 'humidity_min', 'humidity_max',
                                     'airflow_min', 'airflow_max', 'light_min', 'light_max'])

from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]
class WindowClass(QMainWindow, from_class):
  def __init__(self):
    super().__init__()
    pygame.mixer.init()
    self.setupUi(self)
    self.db = DataManager()

    self.system_message_timer = QTimer(self) 
    self.age_timer = QTimer(self)
    

    self.plantData = None
    self.age =0
    self.blink_count = 0

    self.label_system_message.hide()
    self.label_select.hide()
    self.btn_harvest.hide()

    self.io_icons = [self.on_icon_aircon, self.on_icon_heater, self.on_icon_water, self.on_icon_light]
    self.env_labels = [self.label_cur_temp, self.label_cur_humidity, self.label_cur_light]
    self.image = None

    self.btn_log.clicked.connect(self.onClick_show_logWindow)
    self.btn_alarm.clicked.connect(self.onClick_show_alarm)
    self.btn_harvest.clicked.connect(self.onClick_harvest)
    self.btn_massage.clicked.connect(self.onClick_play_massage)
    self.btn_loveVoice.clicked.connect(self.onClick_play_love_voice)

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

      self.age_timer.timeout.connect(self.add_age)
      self.age_timer.start(1000)


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
      self.insert_alarm_data()

  def insert_alarm_data(self):
    log_id = self.db.select_last_id("log_data")
    self.db.insert_data("alarm_data", (f"{log_id}"))

  def insert_log_data(self, cmd_type, cmd_value):
    message_type = cmd_type + str(cmd_value)
    (message_id, message) = self.db.select_data("message_data", ("id", "message") , f"type = {message_type}")
    self.set_system_message(message)

    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    path = self.capture()
    self.db.insert_data("log_data", ("plant_id", "plant_age", "message_id", "date", "path"), (self.plantData.id, self.age, message_id, today, path))
    return
  

  def add_age(self):
    # self.age = (datetime.now() - self.plantData.planted_date).days
    self.age += 1 # 시연을 위한 코드
    if self.age >= self.plantData.need_day:
      self.btn_harvest.show()


  def set_system_message(self, message):
    self.label_system_message.setText(message)
    self.system_message_timer.timeout.connect(self.display_system_message)
    self.system_message_timer.start(1000)


  def display_system_message(self):
    self.label_system_message.setVisible(self.blink_count % 2 == 0)
    self.blink_count += 1
    if self.blink_count >=6:
      self.system_message_timer.stop() 
    return

  def capture(self):
    path = os.path.join("SmartFarmGUI", "record", str(self.plantData.id))
    os.makedirs(path, exist_ok=True)
    file_count = len(glob.glob(os.path.join(path, '*')))
    filename = path+str(file_count) + '.png'
    cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
    return path
  

  def onClick_harvest(self):
    self.age_timer.stop() 
    print('\033[91m'+'onClick_harvest: ' + '\033[0m', "onClick_harvest")
    self.db.update_data("plant_data", ("isComplete",), (True,))
    self.login()

  def onClick_show_logWindow(self):
    log_datas = self.db.select_data(
            table="log_data",
            columns=("log_data.*", "message_data.type", "message_data.message"),
            join="INNER JOIN message_data ON log_data.message_id = message_data.id",
            where=f"log_data.plant_id = {self.plantData.id}"
        )

    logWindow = LogWindowClass(log_datas)
    logWindow.show()
    logWindow.exec_()


  def onClick_show_alarm(self):
    log_datas = self.db.select_data(
      table="log_data",
      columns=("log_data.*", "message_data.message", "message_data.type"),
      join="""
                INNER JOIN message_data ON log_data.message_id = message_data.id
                INNER JOIN alarm_data ON log_data.id = alarm_data.log_id
            """,
      where=f"log_data.plant_id = {self.plantData.id}"
    )

    alarmWindow = AlarmWindowClass(log_datas)
    alarmWindow.show()
    alarmWindow.exec_()
    self.db.delete_data("alarm_data")
  
  def onClick_play_massage(self):
    audio_file = "SmartFarmGUI/resource/massage.mp3"
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    self.farm_manager.request_play_massage()
    return   
  
  def onClick_play_love_voice(self):
    # self.stop_audio()
    audio_file = "SmartFarmGUI/resource/loveVoice.mp3"
    sound = pygame.mixer.Sound(audio_file)
    sound.play()
    self.insert_log_data("SA", 0)
    return

    


if __name__ == "__main__":
  app = QApplication(sys.argv)
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())