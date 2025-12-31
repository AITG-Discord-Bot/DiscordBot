from pydantic import BaseModel

class ForumChannelReqDTO(BaseModel):
    channelid: int
    userid: int