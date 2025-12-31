from pydantic import BaseModel
from typing import Optional

class ServerParamsUpdate(BaseModel):
    modrole: Optional[int] = None
    botmessagechannel: Optional[int] = None
    welcomemessage: Optional[str] = None
    clanmaterole: Optional[int] = None
    clanname: Optional[str] = None
    subnews: Optional[int] = None
    linkrole: Optional[int] = None