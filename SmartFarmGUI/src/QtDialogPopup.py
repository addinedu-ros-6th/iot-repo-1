import glob
import sys
import numpy as np
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from datetime import datetime, time
import os


from_class_select = uic.loadUiType("SmartFarmGUI/ui/select.ui")[0]

class SelectWindow(QDialog, from_class_select):
  def __init__(self, plant_types, db):
    super().__init__()
    self.setupUi(self)
    self.show()

    self.db = db

    for type in plant_types:
      self.select_combo.addItem(type[0])

    self.btn_start.clicked.connect(self.select_plant)

  def select_plant(self):
    select = self.select_combo.currentText()
    
    if select != "":
      self.plant_id = self.db.select_last_id("plant_data")
      path = "SmartFarmGUI/record/" +  str(self.plant_id)
      os.mkdir(path)
    
      today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      self.db.insert_data("plant_data", ("start_date", "plant_type", "isComplete"), (today, select, False))
      self.close()

from_class_log = uic.loadUiType("SmartFarmGUI/ui/log.ui")[0]
class LogWindowClass(QDialog, from_class_log):

  def __init__(self, log_datas):
    super().__init__()
    self.setupUi(self)
    self.btn_search.clicked.connect(self.onClick_search)

    self.log_datas = log_datas

    self.min_day = self.log_datas[0][4]
    self.max_day = self.log_datas[-1][4]
    self.min_day = QDate(self.min_day.year, self.min_day.month, self.min_day.day)
    self.max_day = QDate(self.max_day.year, self.max_day.month, self.max_day.day)

    self.dt_start.setDate(self.min_day)
    self.dt_end.setDate(self.max_day)

    unique_message_ids = list(set(log_entry[3] for log_entry in self.log_datas))
    self.message_data = self.db.get_message_data(unique_message_ids)

    self.cb_status.addItem("ALL")
    for data in self.message_data:
      self.cb_status.addItem(data[1])

    self.show()


  def onClick_search(self):
    status = self.cb_status.currentText()

    min_day = self.dt_start.dateTime().toPyDateTime()
    max_day = self.dt_end.dateTime().toPyDateTime()
    max_day = datetime.combine(max_day.date(), time(23, 59, 59))

    search_data = []
    for log_data in self.log_datas:

      log_date = log_data[4]
      log_status_value = log_data[7]
      log_age_value = log_data[2]
      message = log_data[8]

      if min_day <= log_date <= max_day:
        if status == log_status_value  or status=="ALL":
          data = [
            log_date.strftime('%Y-%m-%d %H:%M'),
            log_status_value,
            str(log_age_value),
            message
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


from_class_alarm = uic.loadUiType("SmartFarmGUI/ui/alarm.ui")[0]
class AlarmWindowClass(QDialog, from_class_alarm):
  def __init__(self, log_datas):
    super().__init__()
    self.setupUi(self)

    self.log_datas = self.db.get_log_data(log_datas)
  
    for log_data in self.log_datas:

      date = log_data[4].strftime('%Y-%m-%d %H:%M')
      age = log_datas[2]
      type = log_datas[1]
      message = log_datas[5]

      row = self.tableWidget.rowCount()
      self.tableWidget.insertRow(row)

      self.tableWidget.setItem(row, 0, QTableWidgetItem(date))
      self.tableWidget.setItem(row, 1, QTableWidgetItem(age))
      self.tableWidget.setItem(row, 2, QTableWidgetItem(type))
      self.tableWidget.setItem(row, 3, QTableWidgetItem(message))
      
from_class_snapshot = uic.loadUiType("SmartFarmGUI/ui/snapshot.ui")[0]


class SnapshotWindowClass(QDialog, QObject, from_class_snapshot):
  request_image_save = pyqtSignal(np.ndarray)
  request_insert_snapshot_data = pyqtSignal(str, str, str)
  def __init__(self, image):
    super.__init__()
    self.show()
    self.image = image
    self.SAVEbutton.clicked.connect(self.capture)

  def capture(self):
    filename = self.request_image_save.emit(self.image)
    to_plant_message = self.message2plant.text()
    now =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.request_insert_snapshot_data.emit(now, to_plant_message, filename)
    self.close()
  
