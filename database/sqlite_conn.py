
import datetime
import sqlite3


class SqliteConn:
   def __init__(self, db_path: str):
      self.db_path = db_path
      self.conn = sqlite3.connect(db_path)
      self.cursor = self.conn.cursor()

   def close(self):
      self.conn.close()

   def commit(self):
      self.conn.commit()

   def rollback(self):
      self.conn.rollback()

   def execute(self, query: str, params: tuple ):
      self.cursor.execute(query, params)
      return self.cursor.fetchall()

   def lastrowid(self):
      return self.cursor.lastrowid
   
   

   def fetchone(self):
      return self.cursor.fetchone()

   def fetchall(self):
      return self.cursor.fetchall()

   def executemany(self, query: str, params: list):
      self.cursor.executemany(query, params)
      return self.cursor.fetchall()

   def executescript(self, query: str):
      self.cursor.executescript(query)
      return self.cursor.fetchall()
