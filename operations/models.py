from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import datetime

class baseModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime = datetime.datetime.now()