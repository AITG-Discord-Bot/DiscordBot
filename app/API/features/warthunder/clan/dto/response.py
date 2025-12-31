from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ThunderClanVacationDTO(BaseModel):
    idx: int
    memberidx: int
    startdate: datetime
    enddate: datetime
    reason: Optional[str]


class ThunderClanMemberDTO(BaseModel):
    idx: int
    clanidx: int
    nick: str
    rating: int
    activity: int
    role: str
    joindate: str
    updated_at: datetime


class ThunderClanVacationResponse(ThunderClanVacationDTO):
    member: Optional[ThunderClanMemberDTO]


class ThunderClanMemberResponse(ThunderClanMemberDTO):
    vacation: list[ThunderClanVacationDTO]
