from API.core import ApiClient
from API.features.server import response as server_res
from . import response as news_res

class WarthunderNewsAPI(ApiClient):
    async def get_latest(self, lang: str = "ko") -> list[news_res.NewsDTO]:
        return await self.request(
            endpoint="/warthunder/news/latest",
            method="GET",
            params={"lang": lang},
            response_model=news_res.NewsDTO,
        )

    async def get_servers(self) -> list[server_res.ServerDTO]:
        return await self.request(
            endpoint="/warthunder/news/servers",
            method="GET",
            response_model=server_res.ServerDTO,
        )