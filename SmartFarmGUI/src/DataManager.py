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

  def delete_data(self, table, where = None, params = None):
    sql = f"DELETE FROM {table}"

    if where:
        sql += f" WHERE {where}"

    print("delete_data: ", sql)
    
    if params:
        self.cursor.execute(sql, params)
    else:
        self.cursor.execute(sql)
    
    self.db.commit()

  def update_data(self, table, columns, params, where = None):
    set_clauses = [f"{column} = %s" for column in columns]
    set_clause_str = ', '.join(set_clauses)

    sql = f"UPDATE {table} SET {set_clause_str}"

    if where:
      sql += f" WHERE {where}"

    print("update_data: ", sql)
    self.cursor.execute(sql, params)
    self.db.commit()

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


  def select_data(self, table, columns= ("*",), where = None, join = None, order = None, limit=None):
    columns_str = ', '.join(columns)

    sql = f"""
      SELECT {columns_str}
      FROM {table}
    """
    if join:
      sql += f" {join}" #inner join, left joint 등 조인에는 종류가 다양하다.
    if where:
      sql += f" WHERE {where}"
    if order:
      sql += f" ORDER BY {order}"
    if limit:
      sql += f" LIMIT {limit}"

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
    

