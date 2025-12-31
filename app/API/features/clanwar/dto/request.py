from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClanwarReqDTO(BaseModel):
    serverid: int
    time: datetime
    ownerid: int
    battlerating: str
    channelid: int
    messageid: int
    description: Optional[str] = None
    threadid: Optional[int] = None
    voicechannelid: Optional[int] = None

class ClanwarPeopleReqDTO(BaseModel):
    userid: int
    usertype: int

__all__ = ['ClanwarPeopleReqDTO', 'ClanwarReqDTO']