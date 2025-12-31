from API.core import ApiClient
from .dto import request as req, response as res


class SupportAPI(ApiClient):
    async def create(self, dto:req.ForumChannelReqDTO) -> res.ForumChannelDTO:
        return await self.request(
            endpoint="/support/forumchannel",
            method="POST",
            response_model=res.ForumChannelDTO,
            json=dto.model_dump(),
        )

    async def get(self, userid: int = None, channelid: int = None) -> res.ForumChannelDTO:
        params = {}
        if userid and channelid:
            raise ValueError("Either userid or channelid must be provided, not both.")
        elif not userid and not channelid:
            raise ValueError("Either userid or channelid must be provided.")
        if userid is not None:
            params["userid"] = userid
        elif channelid is not None:
            params["channelid"] = channelid
        return await self.request(
            endpoint="/support/forumchannel",
            method="GET",
            response_model=res.ForumChannelDTO,
            params=params,
        )

    async def delete(self, channelid: int) -> None:
        return await self.request(
            endpoint="/support/forumchannel",
            method="DELETE",
            params={"channelid": channelid},
        )

supportAPI = SupportAPI()
__all__ = ["supportAPI"]