from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ClanwarPeopleDTO(BaseModel):
    idx: int
    clanwaridx: str
    userid: int
    usertype: int


class ClanwarDTO(BaseModel):
    idx: str
    serverid: int
    channelid: int
    messageid: int
    description: Optional[str]
    battlerating: str
    time: datetime
    ownerid: int
    threadid: Optional[int]
    voicechannelid: Optional[int]
    notified: bool
    cancel_notified: bool
    people: list[ClanwarPeopleDTO]


__all__ = ["ClanwarPeopleDTO", "ClanwarDTO"]