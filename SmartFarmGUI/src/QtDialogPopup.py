import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from DataManager import DataManager
from datetime import datetime, time

log_from_class = uic.loadUiType("SmartFarmGUI/ui/log.ui")[0]
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

        
alarm_from_class = uic.loadUiType("SmartFarmGUI/ui/alarm.ui")[0]


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