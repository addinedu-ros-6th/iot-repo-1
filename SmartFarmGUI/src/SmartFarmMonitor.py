import time
from PyQt5.QtCore import *
import numpy as np
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
    return


class SmartFarmMonitor(QObject):
  request_care = pyqtSignal(str, int)
  update_camera = pyqtSignal(np.ndarray)
  def __init__(self):
    self.classifier = TomatoDiseaseClassifier('SmartFarmAI/src/tomato_vgg16_model.h5')
    
    self.classificationThread = None
    self.detectThread = None

    self.plant_condition = [0, 0, 0]  # 시연용


  def classification_start(self):
    self.classificationThread = MonitoringThread(0.1)
    self.classificationThread.update.connect(self.classification_update)
    self.classificationThread.running = True

  def classification_update(self):
    result_tuple = self.classifier.run()
    if result_tuple == None:
      return

    self.update_camera.emit(result_tuple[1])

    plant_status = result_tuple[0]

    # 시연용
    if plant_status == 0 and self.plant_condition[0] == 0:
      self.request_care.emit('ST', 0)
      self.plant_condition[0] = 1
    elif plant_status == 2 and self.plant_condition[1] == 0:
      self.request_care.emit('ST', 1)
      self.plant_condition[1] = 1
    elif plant_status == 3 and self.plant_condition[2] == 0:
      self.request_care.emit('ST', 2)
      self.plant_condition[2] = 1
    return
  
  def classification_stop(self):
    print('\033[91m'+"Stop classification\033[0m")
    self.classificationThread.running = False
    return


  def detector_start(self):
    model_path = 'SmartFarmAI/src/trained_model.pt'  # YOLO 모델 파일 경로
    self.detector = TomatoDetector(model_path)
    
    self.detectThread = MonitoringThread(0.1)
    self.detectThread.update.connect(self.detector_update)
    self.detectThread.running = True

    return

  def detector_update(self):
    # 감지 결과 얻기
    result_image = self.detector.detect()
    # print('\033[91m'+'result_image: ' + '\033[90m' + "detector_update"+ '\033[0m')
    # 결과 이미지를 화면에 표시
    self.update_camera.emit(result_image)
    return

  def detector_stop(self):
    self.detectThread.running = False
    return



