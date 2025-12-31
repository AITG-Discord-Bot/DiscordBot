from API.core import ApiClient
from .dto import request as req, response as res

class ServerAPI(ApiClient):
    async def set_availability(self, available:bool, serverid: int = None) -> None:
        params = {}
        endpoint = f"/server/availability"
        if serverid is not None:
            params["serverid"] = serverid
        params["availability"] = available
        return await self.request(
            endpoint=endpoint,
            method="POST",
            params=params,
        )

    async def delete_unavailable_servers(self) -> None:
        return await self.request(
            endpoint="/server/availability",
            method="DELETE",
        )

    async def get_clannames(self) -> list[str]:
        return await self.request(
            endpoint=f"/server/clannames",
            method="GET",
        )

    async def get_server(self, serverid: int) -> res.ServerDTO:
        return await self.request(
            endpoint=f"/server/{serverid}",
            method="GET",
            response_model=res.ServerDTO,
        )

    async def create_server(self, serverid: int) -> res.ServerDTO:
        return await self.request(
            endpoint=f"/server/{serverid}",
            method="POST",
            response_model=res.ServerDTO,
        )

    async def patch_server(self, serverid: int, dto: req.ServerParamsUpdate) -> res.ServerDTO:
        return await self.request(
            endpoint=f"/server/{serverid}",
            method="PATCH",
            response_model=res.ServerDTO,
            json=dto.model_dump(exclude_unset=True),
        )

    async def delete_server(self, serverid: int) -> None:
        return await self.request(
            endpoint=f"/server/{serverid}",
            method="DELETE",
        )

    async def get_mod(self, serverid: int) -> int:
        return await self.request(
            endpoint=f"/server/{serverid}/mods",
            method="GET",
        )

serverAPI = ServerAPI()
__all__ = ["serverAPI"]