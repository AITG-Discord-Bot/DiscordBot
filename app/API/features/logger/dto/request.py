from pydantic import BaseModel


class LogChannelReqDTO(BaseModel):
    serverid: int
    logcategory: int
    logchannel: int

class MessageLogReqDTO(BaseModel):
    frommessage: int
    fromchannel: int
    tomessage: int
    tochannel: int