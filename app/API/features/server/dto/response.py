from typing import Optional
from pydantic import BaseModel

class ServerDTO(BaseModel):
    serverid: int
    modrole: Optional[int]
    botmessagechannel: Optional[int]
    welcomemessage: Optional[str]
    clanmaterole: Optional[int]
    clanname: Optional[str]
    subnews: Optional[int]
    newslang: Optional[str]
    linkrole: Optional[int]
    available: bool