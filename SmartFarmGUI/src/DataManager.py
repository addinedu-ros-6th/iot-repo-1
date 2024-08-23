import mysql.connector
from datetime import datetime

class DataManager :

  def __init__(self):

    self.db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234",
            database = "iot"
        )
    
    self.cursor = self.db.cursor()


  def insert_data(self, table, columns, params):
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(params))
    sql = f"""
      INSERT INTO {table} ({columns_str})
      VALUES ({placeholders})
    """
    print("insert_data: ",sql)
    self.cursor.execute(sql, params)
    self.db.commit()


  def select_data(self, table, columns= ("*",), where = None):
    columns_str = ', '.join(columns)

    sql = f"""
      SELECT {columns_str}
      FROM {table}
    """
    if where:
      sql += f" WHERE {where}"

    print("select_data: ", sql)
    self.cursor.execute(sql)
    results = self.cursor.fetchall()
    return results
  
  def select_last_id(self, table):
    sql = f"""
      SELECT id
      FROM {table}
    """
    sql += " ORDER BY id"
    sql += " DESC LIMIT 1"
    print("select_last_id: ", sql)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result[0][0]



  def __del__(self):
    self.db.close()
    self.cursor.close()
    

