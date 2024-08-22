import glob
import sys

import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from DataManager import DataManager
from datetime import datetime, time
import os

log_from_class = uic.loadUiType("iot-repo-1/SmartFarmGUI/ui/log.ui")[0]

class LogWindowClass(QDialog, log_from_class):
  def __init__(self, plant_id):
    super().__init__()
    self.setupUi(self)
    self.db = DataManager()

    self.log_datas = self.db.get_log_data(plant_id)
    self.btn_search.clicked.connect(self.input_search)

    min_day = self.log_datas[0][4]
    max_day = self.log_datas[-1][4]
    min_day = QDate(min_day.year, min_day.month, min_day.day)
    max_day = QDate(max_day.year, max_day.month, max_day.day)

    self.dt_start.setDate(min_day)
    self.dt_end.setDate(max_day)


    unique_message_ids = list(set(log_entry[3] for log_entry in self.log_datas))
    self.message_data = self.db.get_message_data(unique_message_ids)
   
    self.cb_status.addItem("ALL")
    for data in self.message_data:
      self.cb_status.addItem(data[1])

    self.show()

  def input_search(self):
    status = self.cb_status.currentText()

    min_day = self.dt_start.dateTime().toPyDateTime()
    max_day = self.dt_end.dateTime().toPyDateTime()
    max_day = datetime.combine(max_day.date(), time(23, 59, 59))

    search_data = []
    for log_data in self.log_datas:
      log_date = log_data[4]
      
      if min_day <= log_date <= max_day:
        message_id = log_data[3]

        for message in self.message_data:
          if message[0] == message_id:
            if status == message[1] or status=="ALL":
              data = [
                log_data[4].strftime('%Y-%m-%d %H:%M'),
                message[1],
                str(log_data[2]),
                message[2]
              ]

              search_data.append(data)

    self.tableWidget.clearContents()  
    self.tableWidget.setRowCount(0)

    for data in search_data:
      row = self.tableWidget.rowCount()
      self.tableWidget.insertRow(row)

      self.tableWidget.setItem(row, 0, QTableWidgetItem(data[0]))
      self.tableWidget.setItem(row, 1, QTableWidgetItem(data[1]))
      self.tableWidget.setItem(row, 2, QTableWidgetItem(data[2]))
      self.tableWidget.setItem(row, 3, QTableWidgetItem(data[3]))

        
alarm_from_class = uic.loadUiType("iot-repo-1/SmartFarmGUI/ui/alarm.ui")[0]


class AlarmWindowClass(QDialog, alarm_from_class):
    
  def __init__(self, plant_id):
    super().__init__()
    self.setupUi(self)
    self.db = DataManager()


    self.log_datas = self.db.get_log_data(plant_id)
    unique_message_ids = list(set(log_entry[3] for log_entry in self.log_datas))
    self.message_data = self.db.get_message_data(unique_message_ids)

    search_data = []
    for log_data in self.log_datas:
      message_id = log_data[3]

      for message in self.message_data:
        if message[0] == message_id:
          data = [
            log_data[4].strftime('%Y-%m-%d %H:%M'),
            message[1],
            str(log_data[2]),
            message[2]
          ]
          search_data.append(data)

    for data in search_data:
      row = self.tableWidget.rowCount()
      self.tableWidget.insertRow(row)

      self.tableWidget.setItem(row, 0, QTableWidgetItem(data[0]))
      self.tableWidget.setItem(row, 1, QTableWidgetItem(data[1]))
      self.tableWidget.setItem(row, 2, QTableWidgetItem(data[2]))
      self.tableWidget.setItem(row, 3, QTableWidgetItem(data[3]))

class SelectWindowClass(QDialog):

  def __init__(self, plant_types, parent=None):
        super().__init__(parent)
        uic.loadUi('iot-repo-1/SmartFarmGUI/ui/select.ui', self)
        self.show()

        for item in plant_types:
          self.comboBox_select.addItem(item[0])

        self.btn_start.clicked.connect(self.goto_main)

  def goto_main(self):
        self.close()
        
        

class SnapshotWindowClass(QDialog):

    def __init__(self, image, plant_id, parent=None):
        super().__init__(parent)
        self.db = DataManager()
        uic.loadUi('iot-repo-1/SmartFarmGUI/ui/snapshot.ui', self)
        self.show()
        self.plant_id = plant_id
        self.pixmap = QPixmap()
        self.image = image

        self.SAVEbutton.clicked.connect(self.capture)
        self.notSAVEbutton.clicked.connect(self.notsave)

        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w * c, QImage.Format_RGB888)
        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.snapshot.width(), self.snapshot.height(), Qt.KeepAspectRatio)
        # Label에 pixmap 설정
        self.snapshot.setPixmap(self.pixmap)

    def capture(self):

        path = "iot-repo-1/SmartFarmGUI/record/" +  str(self.plant_id)+"/"
        file_count = len(glob.glob(os.path.join(path, '*')))
        filename = path+str(file_count) + '.png'
        cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        to_plant_message = self.message2plant.text()
        now =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.insert_snapshot_data(self.plant_id,now,to_plant_message, filename)

        self.close()

    def notsave(self):
        self.close()