from pydantic import BaseModel


class VoiceChannelDTO(BaseModel):
    """JointoCreate 음성 생성 응답 DTO"""
    serverid: int
    channelid: int

class CreatedVoiceChannelDTO(BaseModel):
    """JointoCreate 음성 생성 응답 DTO"""
    serverid: int
    voicechannel: int

__all__ = ["VoiceChannelDTO", "CreatedVoiceChannelDTO"]