from interactions import *
from common import apirequest


"""
이건 왜 handler 가 아니라 funcs 인가요

그러게요...
그런데 아마 initialize_server 저 함수 때문일거 같습니다. 간단한 코드 몇줄인데 또 따로 handler 로
on_server_join, on_server_remove 로 찢기에는 너무 배보다 배꼽이 커지는거 같아서 그냥 func 로 뒀습니다.

"""


async def initialize_server(bot: Client):
    await apirequest(
        "/server/availability", params={"availability": False}, method="POST"
    )
    for server in bot.guilds:
        json = {"serverid": server.id, "availability": True}
        await apirequest("/server/availability", method="POST", params=json)
    await apirequest("/server/availability", method="DELETE")


async def add_server(server: Guild):
    await apirequest("/server", method="POST", params={"serverid": server.id})


async def remove_server(server: Guild):
    await apirequest(f"/server/{server.id}", method="DELETE", surpress_error=True)
