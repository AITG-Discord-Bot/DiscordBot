from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LogChannelDTO(BaseModel):
    serverid: int
    logcategory: int
    logchannel: Optional[int]

class MessageLogDTO(BaseModel):
    frommessage: int
    fromchannel: int
    tomessage: int
    tochannel: int
    timestamp: datetime