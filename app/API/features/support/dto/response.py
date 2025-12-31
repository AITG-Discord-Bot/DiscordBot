from pydantic import BaseModel

class ForumChannelDTO(BaseModel):
    channelid: int
    userid: int