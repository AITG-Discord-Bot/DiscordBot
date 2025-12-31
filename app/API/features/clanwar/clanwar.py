from API.core import ApiClient
from .dto import request as req, response as res


class ClanwarAPI(ApiClient):
    async def get_clanwar(self) -> list[res.ClanwarDTO]:
        return await self.request(endpoint="/clanwar", method="GET")

    async def create_clanwar(
        self, clanwar: req.ClanwarReqDTO
    ) -> res.ClanwarDTO:
        return await self.request(
            endpoint="/clanwar",
            method="POST",
            response_model=res.ClanwarDTO,
            json=clanwar.model_dump(mode="json"),
        )

    async def get_clanwar_unnotified(self) -> list[res.ClanwarDTO]:
        return await self.request(endpoint="/clanwar/unnotified", method="GET")

    async def get_clanwar_unfinished(self) -> list[res.ClanwarDTO]:
        return await self.request(endpoint="/clanwar/unfinished", method="GET")

    async def get_clanwar_by_idx(self, idx: str) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/{idx}", method="GET", response_model=res.ClanwarDTO
        )

    async def update_clanwar(
        self, idx: str, clanwar: req.ClanwarReqDTO
    ) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/{idx}",
            method="PATCH",
            response_model=res.ClanwarDTO,
            json=clanwar.model_dump(mode="json"),
        )

    async def delete_clanwar(self, idx: str) -> None:
        return await self.request(
            endpoint=f"/clanwar/{idx}",
            method="DELETE",
        )

    async def get_clanwar_by_messageid(self, messageid: int) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/message/{messageid}",
            method="GET",
            response_model=res.ClanwarDTO,
        )

    async def add_people(self, idx: str, people: req.ClanwarPeopleReqDTO) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/people/{idx}",
            method="POST",
            response_model=res.ClanwarDTO,
            json=people.model_dump(),
        )

    async def remove_people(self, idx: str, userid: int) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/people/{idx}/{userid}",
            method="DELETE",
            response_model=res.ClanwarDTO,
        )

    async def get_clanwar_by_people(self, serverid: int, userid: int) -> list[res.ClanwarDTO]:
        return await self.request(
            endpoint=f"/clanwar/server/{serverid}/people/{userid}",
            method="GET",
            response_model=res.ClanwarDTO,
        )

    async def mark_notified(self, idx: str) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/{idx}/notified",
            method="POST",
            response_model=res.ClanwarDTO,
        )

    async def mark_cancel_notified(self, idx: str) -> res.ClanwarDTO:
        return await self.request(
            endpoint=f"/clanwar/{idx}/cancel_notified",
            method="POST",
            response_model=res.ClanwarDTO,
        )

clanwarAPI = ClanwarAPI()

__all__ = ["clanwarAPI"]