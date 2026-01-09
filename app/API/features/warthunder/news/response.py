from datetime import datetime
from pydantic import BaseModel

class NewsDTO(BaseModel):
    idx: int | None
    language: str
    title: str
    link: str
    poster: str
    content: str
    time: datetime