from interactions import *
from API.features.server import serverAPI


"""
이건 왜 handler 가 아니라 funcs 인가요

그러게요...
그런데 아마 initialize_server 저 함수 때문일거 같습니다. 간단한 코드 몇줄인데 또 따로 handler 로
on_server_join, on_server_remove 로 찢기에는 너무 배보다 배꼽이 커지는거 같아서 그냥 func 로 뒀습니다.

"""


async def initialize_server(bot: Client):
    await serverAPI.set_availability(available=False)
    for server in bot.guilds:
        await serverAPI.set_availability(available=True, serverid=server.id)
    await serverAPI.delete_unavailable_servers()


async def add_server(server: Guild):
    await serverAPI.create_server(server.id)


async def remove_server(server: Guild):
    try:
        await serverAPI.delete_server(server.id)
    except:
        pass