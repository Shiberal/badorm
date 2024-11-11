import datetime
from decimal import Decimal
from pydantic import BaseModel
from database.sqlite_conn import SqliteConn
from uuid import UUID
class Operations :
   pydantic_model: BaseModel = None
   sqlite_conn: SqliteConn = None

   def __init__(self, pydantic_model: BaseModel, sqlite_conn: SqliteConn):
      self.pydantic_model = pydantic_model
      self.sqlite_conn = sqlite_conn

   # CREATE transform a pydantic model into a database record
   def create(self, data):
      # Convert datetime.date and datetime.time objects to strings
      processed_data = self.makeItSqliteReadable(data)

      fields = list(processed_data.keys())
      values = ["?" for _ in fields]  # Use parameterized queries with "?"
      query = f"INSERT INTO {self.pydantic_model.__name__} ({', '.join(fields)}) VALUES ({', '.join(values)})"
      dataout = self.sqlite_conn.execute(query, tuple(processed_data.values()))
      self.sqlite_conn.commit()
      return dataout

   # READ reads a record from the database
   # READ reads a record from the database
   def readOne(self, uuid: UUID):
      uuid = str(uuid)
      query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE id = ?"
      dataout = self.sqlite_conn.execute(query, (uuid,))
      # Get the first row and convert it to a dictionary using column names
      if not dataout:
          return None
      columns = [description[0] for description in self.sqlite_conn.cursor.description]
      row_dict = dict(zip(columns, dataout[0]))
      return self.pydantic_model(**row_dict)
   
   def readMany(self, uuid: UUID):
      uuid = str(uuid)
      query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE id = ?"
      dataout = self.sqlite_conn.execute(query, (uuid,))
      return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]
   
   # UPDATE updates a record in the database
   def update(self, uuid: UUID, data: dict):
      uuid = str(uuid)
      processed_data = self.makeItSqliteReadable(data)

      query = f"UPDATE {self.pydantic_model.__name__} SET {', '.join([f'{key} = ?' for key in processed_data.keys()])} WHERE id = ?"
      self.sqlite_conn.execute(query, tuple(processed_data.values()) + (uuid,))
      self.sqlite_conn.commit()
      return True

   # DELETE deletes a record from the database
   def delete(self, uuid: str):
      return self.sqlite_conn.execute(f"DELETE FROM {self.pydantic_model.__name__} WHERE id = ?", (id,))

   # READ ALL reads all records from the database
   def readAll(self):
      query = f"SELECT * FROM {self.pydantic_model.__name__}"
      dataout = self.sqlite_conn.execute(query, tuple())
      return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]

   # READ_BY_FIELD reads all records from the database by a given field
   def readByField(self, field: str, value: str):
      query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE {field} = ?"
      dataout = self.sqlite_conn.execute(query, (value,))
      return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]

   def makeTable(self):
      fields = [f"{key} {self.pydantic_model.model_fields[key].annotation.__name__}" for key in self.pydantic_model.model_fields.keys()]
      #if uuid is in the field make it the primary key and string
      if "uuid" in fields:
         fields[fields.index("uuid")] = "id TEXT PRIMARY KEY"

      return self.sqlite_conn.execute(
         f'CREATE TABLE IF NOT EXISTS {self.pydantic_model.__name__} ({", ".join(fields)})', 
         tuple()
      )

   def makeItSqliteReadable(self, data):
       processed_data = {}
       for key, value in data.items():

          if isinstance(value, datetime.date):
             processed_data[key] = value.isoformat()
          elif isinstance(value, datetime.time):
             processed_data[key] = value.isoformat()
         
          elif isinstance(value, UUID):
             processed_data[key] = str(value)
            
          elif isinstance(value, Decimal  ):
             processed_data[key] = float(value)
             print ("Real is not supported with this dbms, converting to float")


          else:
             processed_data[key] = value
       return processed_data
   
   def lastbydate(self, date: datetime.datetime):
      # #select the last record by date ordered by date
      # query = f"SELECT * FROM {self.pydantic_model.__name__} ORDER BY created_at DESC LIMIT 1"
      query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE created_at = (SELECT MAX(created_at) FROM {self.pydantic_model.__name__})"
      dataout = self.sqlite_conn.execute(query, tuple())
      return self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], dataout[0])))
   
   def readLast(self):
      query = f"SELECT * FROM {self.pydantic_model.__name__} ORDER BY id DESC LIMIT 1"
      dataout = self.sqlite_conn.execute(query, tuple())
      return self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], dataout[0])))
   
   def getByField(self, fields: list[str], values: list[str], limit: int = 100, offset: int = 0,  op: str = "AND"):
      fields_composed = []
      for index,fi in enumerate (fields):
         fields_composed.append(f"{fi} = ?")
         if index < len (fields) - 1:
            fields_composed.append(op)

      query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE " + " ".join(fields_composed) + f" LIMIT {limit} OFFSET {offset}"

      dataout = self.sqlite_conn.execute(query, tuple(values))
      return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]
      