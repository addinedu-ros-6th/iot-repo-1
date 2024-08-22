import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import cv2, imutils
from DataManager import DataManager
import datetime
#from SerialCommunicator import Connector, Receiver, Sender 
import pygame
import numpy as np
import time
import os

from_class = uic.loadUiType("iot-repo-1/SmartFarmGUI/ui/main.ui")[0]

class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec = 0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        count = 0
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False

class WindowClass(QMainWindow, from_class):

  def __init__(self):
    super().__init__()
    pygame.mixer.init()
    self.db = DataManager()
    
    self.setupUi(self)
    self.label_system_message.hide()
    self.btn_harvest.hide()
    self.camera = Camera(self)
    self.count = 0

    self.pixmap = QPixmap()
  
    self.btn_start.clicked.connect(self.onClick_select_crop)
    self.btn_massage.clicked.connect(self.onClick_play_massage)
    self.btn_loveVoice.clicked.connect(self.onClick_play_love_voice)
    self.btn_snapshot.clicked.connect(self.snapshotwindow)
    
    self.cameraStart()
    self.camera.update.connect(self.updateCamera)

    self.environment_parameters = {}

  def snapshotwindow(self):
    if hasattr(self, 'image'):
        window_2 = snapshotui(self.image, self)
        window_2.exec_()

    # 포트와 통신을 위한 Thread 객체 생성
    #self.connector = Connector()
    #self.farm_sensor_polling_thread = Sender(1, self.update_get_env_data)
    #self.receiver = Receiver(self.connector.conn)
    #self.receiver.received_env_value.connect(self.set_env_cur_value)
    #self.receiver.received_env_io_result.connect(self.update_env_io_icon)
#
    #self.login()

  # 키우는 식물 여부에 따라 UI 활성/비활성하고
  # 키우는 식물이 없는 경우 새로운 plant_data를 추가하고
  # 해당 식물의 정보(권장 온도/습도 등)를 가져온다.

  def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

  def updateCamera(self):
        #self.label.setText('Camera Running : ' + str(self.count))
        #self.count += 1
        retval, self.image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            h,w,c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.plantcam.width(), self.plantcam.height())

            self.plantcam.setPixmap(self.pixmap)

        self.count +=1

  def login(self):
    grow_data = self.db.get_growing_plant_data()

    if len(grow_data) == 0 :
      self.init_end_plant_dashboard()

    else: 
      self.init_start_plant_dashboard()


  def init_end_plant_dashboard(self):
    self.toggle_active_ui(False)
    plant_types = self.db.get_plant_types()

    for item in plant_types:
      self.comboBox_select.addItem(item[0])

  def init_start_plant_dashboard(self):

    self.toggle_active_ui(True)
    self.receiver.start()
    self.start_get_env_data()

    # 키우는 식물의 정보를 가져온다. 
    plant_info = self.db.get_growing_plant_info()

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
      

  def onClick_play_love_voice(self):
    # self.stop_audio()
    audio_file = "iot-repo-1/SmartFarmGUI/resource/loveVoice.mp3"
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    return

  def onClick_play_massage(self):
    # self.stop_audio()
    audio_file = "iot-repo-1/SmartFarmGUI/resource/massage.mp3"
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    self.connector.send(b"SA", 1)
    return


  def onClick_select_crop(self):
    select = self.comboBox_select.currentText()
    if select != "":
      self.db.insert_plant_data(select)
    self.init_start_plant_dashboard()
    return


  def toggle_active_ui(self, isGrowing):

    if isGrowing == True:
      self.comboBox_select.hide()
      self.btn_start.hide()
      self.label_select.hide()
      self.btn_massage.show()
      self.btn_loveVoice.show()
      self.btn_snapshot.show()
      self.label_day.show()
      self.label_2.show()

    else :
      self.comboBox_select.show()
      self.btn_start.show()
      self.label_select.show()
      self.btn_massage.hide()
      self.btn_loveVoice.hide()
      self.btn_snapshot.hide()
      self.label_day.hide()
      self.label_2.hide()

  def stop_audio(self):
    if pygame.mixer.music.get_busy():
      pygame.mixer.music.stop()

class snapshotui(QDialog):

    def __init__(self, image, parent=None):
        super().__init__(parent)
        uic.loadUi('iot-repo-1/SmartFarmGUI/ui/snapshot.ui', self)
        self.show()
        self.pixmap = QPixmap()
        self.SAVEbutton.clicked.connect(self.capture)
        self.notSAVEbutton.clicked.connect(self.notsave)

        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w * c, QImage.Format_RGB888)
        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.snapshot.width(), self.snapshot.height(), Qt.KeepAspectRatio)
        # Label에 pixmap 설정
        self.snapshot.setPixmap(self.pixmap)

    def capture(self):
        self.now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.now}.png'

        folder_path = 'iot-repo-1/Snapshot'  # 원하는 폴더 경로로 변경하세요
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # 폴더가 존재하지 않으면 생성
        
        file_path = os.path.join(folder_path, filename)  # 전체 파일 경로 생성

        # QPixmap을 QImage로 변환
        image = self.pixmap.toImage()
        
        # QImage를 파일로 저장
        image.save(file_path, "PNG")
        self.to_plant_message = self.message2plant.text()
        print("파일경로 : ", file_path)
        print("현재 시간 : ",self.now)
        print("메세지 : ", self.to_plant_message)
        self.close()

    def notsave(self):
        self.close()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  
  myWindows = WindowClass()
  myWindows.show()
  sys.exit(app.exec_())