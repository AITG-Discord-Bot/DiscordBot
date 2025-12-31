from API.core import ApiClient
from .dto import dto


class VoiceAPI(ApiClient):
    async def get_jointocreate(self) -> list[dto.VoiceChannelDTO]:
        return await self.request(
            "/voice/jointocreatevoicechannel",
            method="GET",
            response_model=dto.VoiceChannelDTO,
        )

    async def create_jointocreate(self, item: dto.VoiceChannelDTO) -> dto.VoiceChannelDTO:
        return await self.request(
            "/voice/jointocreatevoicechannel",
            method="POST",
            json=item.model_dump(),
            response_model=dto.VoiceChannelDTO,
        )

    async def delete_jointocreate(self, item: dto.VoiceChannelDTO) -> str:
        return await self.request(
            "/voice/jointocreatevoicechannel",
            method="DELETE",
            json=item.model_dump(),
            response_model=dto.VoiceChannelDTO,
        )

    async def get_createdvoicechannels(self) -> list[dto.CreatedVoiceChannelDTO]:
        return await self.request(
            "/voice/created",
            method="GET",
            response_model=dto.CreatedVoiceChannelDTO,
        )

    async def create_createdvoicechannel(self, item: dto.VoiceChannelDTO) -> dto.CreatedVoiceChannelDTO:
        return await self.request(
            "/voice/created",
            method="POST",
            json=item.model_dump(),
            response_model=dto.CreatedVoiceChannelDTO,
        )

    async def delete_createdvoicechannel(self, item: dto.VoiceChannelDTO) -> str:
        return await self.request(
            "/voice/created",
            method="DELETE",
            json=item.model_dump(),
            response_model=dto.CreatedVoiceChannelDTO,
        )

voiceApi = VoiceAPI()

__all__ = ["voiceApi"]