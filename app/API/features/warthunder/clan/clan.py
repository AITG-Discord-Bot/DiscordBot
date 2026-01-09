from API.core import ApiClient
from .dto import response as res, request as req

class WarthunderClanAPI(ApiClient):
    async def verify_name(self, name: str) -> bool:
        return await self.request(
            endpoint="/warthunder/clan/verify",
            method="GET",
            params={"clanname": name},
        )

    async def get_members(self, clanname: str) -> list[res.ThunderClanMemberResponse]:
        return await self.request(
            endpoint="/warthunder/clan/members",
            method="GET",
            params={"clanname": clanname},
            response_model=res.ThunderClanMemberResponse,
        )

    async def get_member(self, clanname: str, membernick: str) -> res.ThunderClanMemberResponse:
        return await self.request(
            endpoint=f"/warthunder/clan/{clanname}/member/{membernick}",
            method="GET",
            response_model=res.ThunderClanMemberResponse,
        )

    async def get_vacation(self, clanname: str) -> list[res.ThunderClanVacationResponse]:
        return await self.request(
            endpoint=f"/warthunder/clan/{clanname}/vacation",
            method="GET",
            response_model=res.ThunderClanVacationResponse,
        )

    async def add_vacation(self, vacation: req.ThunderClanVacationDTO) -> res.ThunderClanVacationResponse:
        return await self.request(
            endpoint="/warthunder/clan/vacation",
            method="POST",
            response_model=res.ThunderClanVacationResponse,
            json=vacation.model_dump(mode="json"),
        )

    async def delete_vacation(self, clanname: str, membernick: str) -> res.ThunderClanVacationResponse:
        return await self.request(
            endpoint=f"/warthunder/clan/{clanname}/vacation/{membernick}",
            method="DELETE",
            response_model=res.ThunderClanVacationResponse,
        )

