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
    
    # self.mydb = mysql.connector.connect(
    #   host = '192.168.0.215',
    #   user = "remote",
    #   password = "1234",
    #   database = "iot",
    #   port=3306
    # )
    
    self.cursor = self.mydb.cursor()

  def get_default_update_sql(self, table, params):
    set_clause = f"{params[0]} = %s"
    sql = f"""
      UPDATE {table}
      SET {set_clause}
    """
    return sql, (params[1],)
  
  def update_plant_data(self, params = ("*",)):
    sql, values = self.get_default_update_sql("plant_data", params)
    self.cursor.execute(sql, values)
    print("*********************" + sql + "," + str(values[0]))
    self.mydb.commit()
  
  def update_plant_complete(self, plant_data_id):
    sql = """
    UPDATE plant_data
    SET isComplete = 1
    WHERE plant_id = %s
    """
    self.cursor.execute(sql, (plant_data_id,))
    self.mydb.commit()



  def get_defualt_insert_sql(self, table, param_tuple):
    columns = ', '.join(param_tuple)
    sql = f"""
      INSERT INTO {table} ({columns})
      VALUES 
    """
    return sql

  def insert_plant_data(self, type):
    today = datetime.now()

    sql = f"""
      INSERT INTO plant_data (start_date, plant_type, isComplete)
      VALUES (%s, %s, %s)
    """

    self.cursor.execute(sql, (today, type, False))
    self.mydb.commit()

  def insert_snapshot_data(self, plant_id, now, message, path):
    sql = f"""
      INSERT INTO snapshot_data (plant_id, date, custom_message, path)
      VALUES (%s, %s, %s, %s)
    """
    self.cursor.execute(sql, (plant_id, now, message, path))
    self.mydb.commit()
    

  def insert_log_data(self, log_data_tuple):
    datas = ', '.join(log_data_tuple)
    sql = self.get_defualt_insert_sql("log_data", ("plant_id", "plant_age", "message_id", "date", "path"))
    sql += f" ({datas})"

    print(sql)

    self.cursor.execute(sql)
    self.mydb.commit()

  def insert_alarm_data(self):
    sql = self.get_defualt_insert_sql("alarm_data", ("log_id",))
    sql += "(" + str(self.get_last_id("log_data")) + ")"
    self.cursor.execute(sql)
    self.mydb.commit()

  def get_defualt_select_sql(self, table, param_tuple):
    columns = ', '.join(param_tuple)
    sql = f"""
      SELECT {columns}
      FROM {table}
    """
    return sql
  
    
  def get_log_data(self, plant_id):
    sql = self.get_defualt_select_sql("log_data", ("*",))
    sql += f" WHERE plant_id = {plant_id}"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result


  def get_last_id(self, table):
    sql = self.get_defualt_select_sql(table, ("id", ))
    sql += " ORDER BY id"
    sql += " DESC LIMIT 1"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result[0][0]


  def get_log_message(self, status):
    sql = self.get_defualt_select_sql("message_data", ("*",))
    sql += f" WHERE status = \"{status}\""
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result[0]
  

  def get_message_data(self, ids):
    placeholders = ', '.join(['%s'] * len(ids))
    
    sql = self.get_defualt_select_sql("message_data", ("*",))
    sql += f" WHERE id IN ({placeholders})"
    print(sql)
    self.cursor.execute(sql, ids)
    result = self.cursor.fetchall()
    return result


  def get_plant_info(self):
    grawing_plant_data = self.get_selected_plant_data()
    plant_type = grawing_plant_data[0][2]

    sql = self.get_defualt_select_sql("plant_info", ("*",))
    sql += f" WHERE plant_type = \"{plant_type}\""

    self.cursor.execute(sql)
    
    result = self.cursor.fetchall()
    return result[0]
  

  def get_selected_plant_data(self):
    sql = self.get_defualt_select_sql("plant_data", ("*",))
    sql += " WHERE isComplete = FALSE"
    sql += " ORDER BY start_date"
    sql += " DESC LIMIT 1"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result
  
  def get_plant_types(self):
    sql = self.get_defualt_select_sql("plant_info", ("plant_type",))
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result
  

  def get_growing_plant_data(self, params= ("*",)):
    sql = self.get_defualt_select_sql("plant_data", params)
    sql += " WHERE isComplete = FALSE"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result

  def __del__(self):
    self.mydb.close()
    self.cursor.close()
