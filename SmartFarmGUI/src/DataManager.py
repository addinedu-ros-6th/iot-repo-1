import mysql.connector
from datetime import datetime

class DataManager:

  def __init__(self):
    self.mydb = mysql.connector.connect(
            host = "192.168.0.38",
            user = "remote",
            password = "1234",
            database = "iot"
        )
    #self.mydb = mysql.connector.connect(
    #        host = "localhost",
    #        user = "root",
    #        password = "1722",
    #        database = "amrbase"
    #    )
    
    self.cursor = self.mydb.cursor()


  def insert_plant_data(self, type):
    today = datetime.now()

    sql = f"""
      INSERT INTO plant_data (start_date, plant_type, isComplete)
      VALUES (%s, %s, %s)
    """

    self.cursor.execute(sql, (today, type, False))
    self.mydb.commit()


  def get_defualt_sql(self, table, param_tuple):
    columns = ', '.join(param_tuple)
    sql = f"""
      SELECT {columns}
      FROM {table}
    """
    return sql
  
  def get_growing_plant_info(self):
    grawing_plant_data = self.get_selected_plant_data()
    plant_type = grawing_plant_data[0][2]

    sql = self.get_defualt_sql("plant_info", ("*",))
    sql += f" WHERE plant_type = \"{plant_type}\""

    self.cursor.execute(sql)
    
    result = self.cursor.fetchall()
    return result[0]
  
  def get_selected_plant_data(self):
    sql = self.get_defualt_sql("plant_data", ("*",))
    sql += " WHERE isComplete = FALSE"
    sql += " ORDER BY start_date"
    sql += " DESC LIMIT 1"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result
  
  def get_plant_types(self):
    sql = self.get_defualt_sql("plant_info", ("plant_type",))
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result
  
  def get_growing_plant_data(self):
    sql = self.get_defualt_sql("plant_data", ("*",))
    sql += " WHERE isComplete = FALSE"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result
  
    
  def __del__(self):
    self.mydb.close()
    self.cursor.close()
