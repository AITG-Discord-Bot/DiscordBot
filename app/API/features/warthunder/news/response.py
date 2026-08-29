from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class NewsDTO(BaseModel):
    idx: Optional[int] = None
    newslang: Optional[str] = None
    language: str
    title: str
    link: str
    poster: str
    content: str
    time: datetime