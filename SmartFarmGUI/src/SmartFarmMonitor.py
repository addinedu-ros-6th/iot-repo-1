import time
from PyQt5.QtCore import *
import numpy as np


# import SmartFarmMonitor as sf
from SmartFarmAI.src.final_classification import TomatoDiseaseClassifier
from SmartFarmAI.src.final_detect import TomatoDetector



class MonitoringThread(QThread):
  update = pyqtSignal()

  def __init__(self, sec=0, parent=None):
    super().__init__()
    self.main = parent
    self.running = False
    self.sec = sec
    self.tomatoStatuCounts = [0, 0, 0]

  def run(self):
    while self.running == True:
      self.update.emit()
      time.sleep(self.sec)

  def stop(self):
    self.running = False
    self.quit()  # Tell the event loop to exit
    self.wait() 
    return


class SmartFarmMonitor(QObject):
  request_care = pyqtSignal(str, int)
  update_camera = pyqtSignal(np.ndarray)
  def __init__(self, parent):
    super().__init__(parent)
    self.classifier = TomatoDiseaseClassifier('SmartFarmAI/src/tomato_vgg16_model.h5')
    self.detector = TomatoDetector('SmartFarmAI/src/trained_model.pt')

    self.classificationThread = MonitoringThread(0.1)
    self.classificationThread.update.connect(self.classification_update)
    self.detectThread = MonitoringThread(0.1)
    self.detectThread.update.connect(self.detector_update)

    self.plant_condition = [0, 0, 0]  # 시연용


  def classification_start(self):
    print('\033[91m'+'classification_start: ' + '\033[92m', "classification_start" + '\033[0m')
    self.classificationThread.running = True
    self.classificationThread.start()




  def classification_update(self):
    # print('\033[91m'+'classification_update: ' + '\033[92m', "classification_update" + '\033[0m')

    result_tuple = self.classifier.run()
    if result_tuple == None:
      return

    self.update_camera.emit(result_tuple[1])

    plant_status = result_tuple[0]

    # 시연용-------------
    # 0 - 질병
    # 1 - 해충
    # 2 - 노란잎
    print('\033[91m'+'plant_status: ' + '\033[92m', plant_status)
    if plant_status == 0 and self.plant_condition[0] == 0:
      self.tomatoStatuCounts[0] += 1
      if self.tomatoStatuCounts[0] > 200:
        self.request_care.emit('ST', 0) 
        self.plant_condition[0] = 1
        print('\033[91m'+'plant_condition: ' + '\033[92m', plant_status)
      
    elif plant_status == 2 and self.plant_condition[1] == 0:
      self.tomatoStatuCounts[1] += 1
      if self.tomatoStatuCounts[1] > 200:
        self.request_care.emit('ST', 1)
        self.plant_condition[1] = 1
        print('\033[91m'+'plant_condition: ' + '\033[92m', plant_status)

    elif plant_status == 3 and self.plant_condition[2] == 0:
      self.tomatoStatuCounts[2] += 1
      if self.tomatoStatuCounts[2] > 200:
        self.request_care.emit('ST', 2)
        self.plant_condition[2] = 1
        print('\033[91m'+'plant_condition: ' + '\033[92m', plant_status)
    return
  
  def classification_stop(self):
    print('\033[91m'+"Stop classification\033[0m")
    self.classificationThread.stop()
    return


  def detector_start(self):
    print('\033[91m'+'detector_start: ' + '\033[92m', "detector_start" +'\033[0m')
    self.detectThread.running = True
    self.detectThread.start()
    return

  def detector_update(self):
    print('\033[91m'+'detector_update: ' + '\033[92m', "detector_update" +'\033[0m')

    # 감지 결과 얻기
    result_image = self.detector.detect()
    # print('\033[91m'+'result_image: ' + '\033[90m' + "detector_update"+ '\033[0m')
    # 결과 이미지를 화면에 표시
    self.update_camera.emit(result_image)
    return

  def detector_stop(self):
    print('\033[91m'+'detector_stop: ' + '\033[92m', "detector_stop" +'\033[0m')
    self.detectThread.stop()
    return



