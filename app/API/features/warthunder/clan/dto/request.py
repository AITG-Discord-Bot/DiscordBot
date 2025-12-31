from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ThunderClanVacationDTO(BaseModel):
    memberidx: int
    enddate: datetime
    reason: str


__all__ = ["ThunderClanVacationDTO"]