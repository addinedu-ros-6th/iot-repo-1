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


from_class_log = uic.loadUiType("SmartFarmGUI/ui/log.ui")[0]
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
