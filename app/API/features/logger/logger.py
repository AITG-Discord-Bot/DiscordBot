from API.core import ApiClient
from .dto import request as req, response as res


class LoggerAPI(ApiClient):
    async def get_all(self) -> list[res.LogChannelDTO]:
        return await self.request(
            endpoint="/logger/channels", method="GET", response_model=res.LogChannelDTO
        )

    async def create_logchannel(
        self, logchannel: req.LogChannelReqDTO
    ) -> res.LogChannelDTO:
        return await self.request(
            endpoint="/logger/channels",
            method="POST",
            response_model=res.LogChannelDTO,
            json=logchannel.model_dump(),
        )

    async def get_server_logchannels(self, serverid: int) -> list[res.LogChannelDTO]:
        return await self.request(
            endpoint=f"/logger/channels/{serverid}",
            method="GET",
            response_model=res.LogChannelDTO,
        )

    async def get_logchannel_by_category(
        self, serverid: int, categoryid: int
    ) -> res.LogChannelDTO:
        return await self.request(
            endpoint=f"/logger/channels/{serverid}/{categoryid}",
            method="GET",
            response_model=res.LogChannelDTO,
        )

    async def delete_logchannel(self, serverid: int, categoryid: int) -> None:
        return await self.request(
            endpoint=f"/logger/channels/{serverid}/{categoryid}",
            method="DELETE",
        )

    async def add_message(self, logmessage: req.MessageLogReqDTO) -> res.MessageLogDTO:
        return await self.request(
            endpoint="/logger/messagelog",
            method="POST",
            json=logmessage.model_dump(),
            response_model=res.MessageLogDTO,
        )

    async def add_message_bulk(
        self, logmessages: list[req.MessageLogReqDTO]
    ) -> list[res.MessageLogDTO]:
        json_payload = [logmessage.model_dump() for logmessage in logmessages]
        return await self.request(
            endpoint="/logger/messagelog/bulk",
            method="POST",
            json=json_payload,
            response_model=res.MessageLogDTO,
        )

    async def get_log_by_messageid(self, messageid: int) -> res.MessageLogDTO:
        return await self.request(
            endpoint=f"/logger/messagelog/{messageid}",
            method="GET",
            response_model=res.MessageLogDTO,
        )

    async def delete_old_logs(self) -> None:
        return await self.request(
            endpoint=f"/logger/messagelog/old",
            method="DELETE",
        )


loggerAPI = LoggerAPI()

__all__ = ["loggerAPI"]
