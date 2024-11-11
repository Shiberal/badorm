import datetime
from decimal import Decimal
from pydantic import BaseModel
from database.sqlite_conn import SqliteConn
from uuid import UUID
import re

class Operations:
    def __init__(self, pydantic_model: BaseModel, sqlite_conn: SqliteConn):
        self.pydantic_model = pydantic_model
        self.sqlite_conn = sqlite_conn
        # Validate table name to prevent SQL injection
        if not self._is_valid_identifier(pydantic_model.__name__):
            raise ValueError("Invalid table name")

    def _is_valid_identifier(self, identifier: str) -> bool:
        # Check if identifier follows valid SQL identifier rules
        pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        return bool(pattern.match(identifier))

    def _validate_field_names(self, fields: list[str]) -> None:
        # Validate field names against model fields
        valid_fields = set(self.pydantic_model.model_fields.keys())
        for field in fields:
            if not self._is_valid_identifier(field) or field not in valid_fields:
                raise ValueError(f"Invalid field name: {field}")

    def create(self, data):
        processed_data = self.makeItSqliteReadable(data)
        fields = list(processed_data.keys())
        self._validate_field_names(fields)
        
        placeholders = ["?" for _ in fields]
        query = f"INSERT INTO {self.pydantic_model.__name__} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        dataout = self.sqlite_conn.execute(query, tuple(processed_data.values()))
        self.sqlite_conn.commit()
        return dataout

    def readByField(self, field: str, value: str):
        # Validate field name
        self._validate_field_names([field])
        
        query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE {field} = ?"
        dataout = self.sqlite_conn.execute(query, (value,))
        return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]

    def getByField(self, fields: list[str], values: list[str], limit: int = 100, offset: int = 0, op: str = "AND"):
        # Validate field names
        self._validate_field_names(fields)
        
        # Validate operator
        if op not in ["AND", "OR"]:
            raise ValueError("Invalid operator. Must be 'AND' or 'OR'")
        
        # Validate limit and offset
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Invalid limit value")
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("Invalid offset value")

        fields_composed = []
        for index, fi in enumerate(fields):
            fields_composed.append(f"{fi} = ?")
            if index < len(fields) - 1:
                fields_composed.append(op)

        query = f"SELECT * FROM {self.pydantic_model.__name__} WHERE " + " ".join(fields_composed) + f" LIMIT ? OFFSET ?"
        values = list(values) + [limit, offset]

        dataout = self.sqlite_conn.execute(query, tuple(values))
        return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]

    def makeTable(self):
        fields = []
        for key, field in self.pydantic_model.model_fields.items():
            if not self._is_valid_identifier(key):
                raise ValueError(f"Invalid field name: {key}")
            
            field_type = field.annotation.__name__
            if key == "id" and field_type.lower() == "uuid":
                fields.append("id TEXT PRIMARY KEY")
            else:
                fields.append(f"{key} {field_type}")

        query = f'CREATE TABLE IF NOT EXISTS {self.pydantic_model.__name__} ({", ".join(fields)})'
        return self.sqlite_conn.execute(query, tuple())

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
    def delete(self, uuid: UUID):
        uuid = str(uuid)
        query = f"DELETE FROM {self.pydantic_model.__name__} WHERE id = ?"
        self.sqlite_conn.execute(query, (uuid,))
        self.sqlite_conn.commit()
        return True

    # READ ALL reads all records from the database
    def readAll(self):
        query = f"SELECT * FROM {self.pydantic_model.__name__}"
        dataout = self.sqlite_conn.execute(query, tuple())
        return [self.pydantic_model(**dict(zip([column[0] for column in self.sqlite_conn.cursor.description], row))) for row in dataout]

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
      