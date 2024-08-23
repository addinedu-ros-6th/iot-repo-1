import glob
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2, imutils
from DataManager import DataManager
from SerialCommunicator import Connector, Receiver, Sender 
from QtDialogPopup import AlarmWindowClass, LogWindowClass,SelectWindowClass ,SnapshotWindowClass, SelectWindowClass
import pygame
import os
from datetime import datetime, timedelta
import time
# import numpy as np
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# from ultralytics import YOLO
from SmartFarmAI.src.final_classification import TomatoDiseaseClassifier
from SmartFarmAI.src.final_detect import TomatoDetector

class MonitoringThread(QThread):
  update = pyqtSignal()

  def __init__(self, sec=0, parent=None):
    super().__init__()
    self.main = parent
    self.running = True
    self.sec = sec

  def run(self):
    while self.running == True:
        self.update.emit()
        time.sleep(self.sec)

  def stop(self):
    self.running = False

from_class = uic.loadUiType("SmartFarmGUI/ui/main.ui")[0]

class WindowClass(QMainWindow, from_class):

  def __init__(self):
    super().__init__()
    pygame.mixer.init()
    self.db = DataManager()

    # 잎파리 테스트
    self.classificationThread = MonitoringThread(0.1)
    self.classificationThread.update.connect(self.classification_update)
    self.classification_start()

    self.ageThread = MonitoringThread(2)
    self.ageThread.update.connect(self.age_update)
    self.age_start()

    self.setupUi(self)
    self.timer = QTimer(self) 
    self.blink_count = 0

    self.label_system_message.hide()
    self.btn_harvest.hide()
    self.pixmap = QPixmap()
    
    self.btn_massage.clicked.connect(self.onClick_play_massage)
    self.btn_loveVoice.clicked.connect(self.onClick_play_love_voice)
    self.btn_alarm.clicked.connect(self.onClick_open_alarm)
    self.btn_log.clicked.connect(self.onClick_open_log)
    self.btn_snapshot.clicked.connect(self.onClick_open_snapshot)

    self.plant_age = 0
    self.plant_id = 0
    self.plant_need_day = 0
    self.environment_parameters = {}

    # 포트와 통신을 위한 Thread 객체 생성
    self.connector = Connector()
    self.farm_sensor_polling_thread = Sender(2, self.update_get_env_data)
    self.receiver = Receiver(self.connector.conn)
    self.receiver.received_env_value.connect(self.set_env_cur_value)
    self.receiver.received_env_io_result.connect(self.update_env_io_icon)
    self.receiver.request_log.connect(self.insert_db_log_data)

    self.login()

  def open_select_ui(self):
    plant_types = self.db.get_plant_types()
    select_window = SelectWindowClass(plant_types)
    select_window.exec_()
    self.login()
   
  def login(self):
    growing_plant_data = self.db.get_growing_plant_data()
    
    if len(growing_plant_data) == 0 :
      self.init_end_plant_dashboard()

    else: 
      growing_plant_data = growing_plant_data[0]
      self.plant_id = growing_plant_data[0]
      self.plant_age = (datetime.now() - growing_plant_data[1]).days
      self.init_start_plant_dashboard()


  def init_end_plant_dashboard(self):
    self.toggle_active_ui(False)
    self.open_select_ui()
    

  def init_start_plant_dashboard(self):

    self.toggle_active_ui(True)
    self.receiver.start()
    self.start_get_env_data()
    self.label_day.setText(str(self.plant_age))

    # 키우는 식물의 정보를 가져온다. 
    plant_info = self.db.get_plant_info()

    self.plant_need_day = plant_info[1]

    # 권장 환경 범위값 참조.
    self.environment_parameters = {
      "temperature": {
          "min": plant_info[3],
          "max": plant_info[4],
          "current_label": self.label_cur_temp,
          "inc_io": 1,
          "dec_io": 0,
      },
      
      "humidity": {
          "min": plant_info[5],
          "max": plant_info[6],
          "current_label": self.label_cur_humidity,
          "inc_io": 2,
          "dec_io": None,
      },

      "light": {
          "min": plant_info[9],
          "max": plant_info[10],
          "current_label": self.label_cur_light,
          "inc_io": 3,
          "dec_io": None,
      }
    }

    # 권장 환경 값 설정 및 UI 표시
    recommend_temperature = int((self.environment_parameters["temperature"]["min"] + self.environment_parameters["temperature"]["max"]) / 2)
    recommend_humidity = int((self.environment_parameters["humidity"]["min"] + self.environment_parameters["humidity"]["max"]) / 2)
    recommend_light = int((self.environment_parameters["light"]["min"] + self.environment_parameters["light"]["max"]) / 2)
    self.label_recom_temp.setText("/ " + str(recommend_temperature))
    self.label_recom_humidity.setText("/ " + str(recommend_humidity))
    self.label_recom_light.setText("/ " + str(recommend_light))
  
  
  # 온도/습도/빛의 값이 변경될때마다 호출
  def set_env_cur_value(self, data):
    self.label_cur_temp.setText(str(data[0]))
    self.label_cur_humidity.setText(str(data[1]))
    self.label_cur_light.setText(str(data[2]))
    self.update_env_text_color()

  
  # 로그 메시지를 화면에 출력한다.
  def insert_db_log_data(self, event_type, event_value):

    status = ""

    if event_type == "SE":
      if event_value == 0 and self.on_icon_aircon.isVisible() == False:
        status = "hot"
      elif event_value == 1 and self.on_icon_heater.isVisible() == False:
        status = "cold"
      elif event_value == 2 and self.on_icon_water.isVisible() == False:
        status = "thirsty"
      elif event_value == 3 and self.on_icon_light.isVisible() == False:
        status = "dork"

    elif event_type == "ST":
      if event_value == 0 : # 치료제
        status = "medicine"
      elif event_value == 1:
        status = "bug"
      elif event_value == 2:
        status = "yellow"
    
    elif event_type == "SA":
      if event_value == 0:
        status = "confession"
      elif event_value == 1:
        status = "love"


    if status != "":
      log_message_data =  self.db.get_log_message(status)
      log_message_id = log_message_data[0]
      now = datetime.now().strftime("'%Y-%m-%d %H:%M:%S'")
      
      self.label_system_message.setText(log_message_data[2])
      self.blink_count = 0
      self.timer.timeout.connect(self.display_log_message)
      self.timer.start(1000)

      path = self.capture()
      log_data = (str(self.plant_id), str(self.plant_age), str(log_message_id), now, "'"+path+"'")
      self.db.insert_log_data(log_data)
      self.db.insert_alarm_data()

  def display_log_message(self):
    self.label_system_message.setVisible(self.blink_count % 2 == 0)
    self.blink_count += 1
    if self.blink_count >=6:
      self.timer.stop() 
  
  def capture(self):
    path = "SmartFarmGUI/record/" +  str(self.plant_id)+"/"
    file_count = len(glob.glob(os.path.join(path, '*')))
    filename = path+str(file_count) + '.png'
    cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
    return path
  
  def age_start(self):
    self.ageThread.running = True
    self.ageThread.start()

  def age_stop(self):
    self.ageThread.running = False

  def age_update(self): 
   
    start_day = self.db.get_growing_plant_data(("start_date",))[0][0] # 시연을 위한 코드
    start_day = start_day - timedelta(days=1)
    start_day_str = start_day.strftime('%Y-%m-%d %H:%M:%S')
    self.db.update_plant_data(("start_date",start_day_str))
    self.plant_age = (datetime.now() - start_day).days

    print("age_update: ",'\033[91m'+'현재 나이:' +'\033[90m', str(self.plant_age) +'\033[0m')

    self.label_day.setText(str(self.plant_age))
    if self.plant_need_day <= self.plant_age:
      self.classification_stop()


  def detector_start(self):
    print('\033[91m'+'수확 가능 기간:\033[0m')
    self.detectThread.running = True
    model_path = 'SmartFarmAI/src/trained_model.pt'  # YOLO 모델 파일 경로
    self.detector = TomatoDetector(model_path)
    self.detectThread.start()
  

  def detector_stop(self):
    self.detectThread.running = False


  def detector_update(self):
    # 감지 결과 얻기
    result_image = self.detector.detect()
    # print('\033[91m'+'result_image: ' + '\033[90m' + "detector_update"+ '\033[0m')
    # 결과 이미지를 화면에 표시
    self.update_camera(result_image)
    

  def classification_start(self):
    print('\033[91m'+'작물 성장 기간:\033[0m')
    self.classificationThread.running = True
    self.classifier = TomatoDiseaseClassifier('SmartFarmAI/src/tomato_vgg16_model.h5')
    self.classificationThread.start()

  def classification_stop(self):
    self.classificationThread = False

    # 열매 수확 가능 판단.
    self.detectThread = MonitoringThread(0.1)
    self.detectThread.update.connect(self.detector_update)
    self.detector_start()
    return

  def classification_update(self):
    result_tuple = self.classifier.run() # 0 이 상태값
    
    plant_status = result_tuple[0]
    # 이 값으로 온다.
      # 0 - 치료제
      # 1 - 무동작
      # 2 - 가습기
      # 3 - 영양제
    self.update_camera(result_tuple[1])
    return
  

  # 딥러닝에서 이미지 파일을 받아올 예정.
  def update_camera(self, image):
    if image is None:
      return


    self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    h, w, c = self.image.shape
    qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

    self.pixmap = self.pixmap.fromImage(qimage)
    self.pixmap = self.pixmap.scaled(self.label_view.width(), self.label_view.height())
    self.label_view.setPixmap(self.pixmap)

    
  # 환경의 수치 텍스트 색상 변경
  # 냉방/난방/물주기 ON/OFF
  def update_env_text_color(self):

    for param, details in self.environment_parameters.items():
      min_value = details["min"]
      max_value = details["max"]
      current_label = details["current_label"]

      # 환경 수치가 권장 수치 범위 내에 있는지 체크한다.
      # 높을 경우 해당 환경의 수치를 올리는 io를 on하고 내리는 io를 on
      # 낮을 경우 해당 환경의 수치를 내리는 io를 on하고 올리는 io를 off
      # 권장 범위 안이라면 올리고 내리는 io 둘다 off

      cur_value = float(current_label.text())
      if cur_value <= min_value:
        current_label.setStyleSheet("color: blue;")
        self.update_env_io_control(details['inc_io'], details['dec_io'], True)

      elif cur_value <= max_value:
        current_label.setStyleSheet("color: red;")
        self.update_env_io_control(details['dec_io'], details['inc_io'], True)

      else:
        current_label.setStyleSheet("color: black;")
        if details['inc_io'] != None:
          self.connector.send(b'EE', details['inc_io'])
          self.connector.send(b'EE', details['dec_io'])

  def update_env_io_control(self, inc, dec, isUp):

    if isUp == True:
      # 수치를 올리는 io를 on 하고 내리는 io를 off 한다.
      on_io = inc
      off_io = dec
    elif isUp == False:
      on_io = dec
      off_io = inc
    
    if inc != None:
      self.connector.send(b'SE', on_io)
    if dec != None:
      self.connector.send(b'EE', off_io)


  # 아두이노에서 on/off 신호를 받으면 해당 io의 아이콘을 활성/비활성화 한다.
  def update_env_io_icon(self, control_type, isOn):
    if control_type == 0:
      self.on_icon_aircon.setVisible(isOn)
    elif control_type == 1:
      self.on_icon_heater.setVisible(isOn)
    elif control_type == 2:
      self.on_icon_water.setVisible(isOn)
    elif control_type == 3:
      self.on_icon_light.setVisible(isOn)


  # 멀티스레드의 run을 실행한다.
  def start_get_env_data(self):
    self.farm_sensor_polling_thread.running = True
    self.farm_sensor_polling_thread.start()
    return

  # 멀티스레드의 run을 정지한다.
  def stop_get_env_data(self):
    self.farm_sensor_polling_thread.running = False
    return

  # 1초마다 스마트팜의 환경 데이터를 요청한다.  
  def update_get_env_data(self):
    self.connector.send(b"GE")
    return


  # 치료
  def request_plant_treatment(self, status):
    print("request_plant_treatment")
    if status == 0: # 치료제(감염)
      self.connector.send(b"ST", 0)
    elif status == 1: # 가습기 (해충)
      self.connector.send(b'ST', 1)
    elif status == 2: # 영양제 (노란잎)
      self.connector.send(b'ST', 2)
  
  def onClick_open_snapshot(self):
    if hasattr(self, 'image'):
        window_2 = SnapshotWindowClass(self.image, self.plant_id)
        window_2.exec_()

  def onClick_open_alarm(self):
    alarmWindow = AlarmWindowClass(self.plant_id)
    alarmWindow.show()
    alarmWindow.exec_()

  def onClick_open_log(self):
    logWindow = LogWindowClass(self.plant_id)
    logWindow.show()
    logWindow.exec_()

  def onClick_play_love_voice(self):
    # self.stop_audio()
    audio_file = "SmartFarmGUI/resource/loveVoice.mp3"
    sound = pygame.mixer.Sound(audio_file)
    sound.play()
    return

  # 연달아 실행할때 문제있음.
  def onClick_play_massage(self):
    # self.stop_audio()
    audio_file = "SmartFarmGUI/resource/massage.mp3"
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    self.connector.send(b"SA", 1)
    return


  def toggle_active_ui(self, isGrowing):

    if isGrowing == True:
      self.label_select.hide()
      self.btn_massage.show()
      self.btn_loveVoice.show()
      self.btn_snapshot.show()
      self.label_day.show()
      self.label_2.show()

    else :
      self.label_select.show()
      self.btn_massage.hide()
      self.btn_loveVoice.hide()
      self.btn_snapshot.hide()
      self.label_day.hide()
      self.label_2.hide()

  def stop_audio(self):
    if pygame.mixer.music.get_busy():
      pygame.mixer.music.stop()



if __name__ == "__main__":
  app = QApplication(sys.argv)
  
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())