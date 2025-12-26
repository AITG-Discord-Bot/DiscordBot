import asyncio

from interactions import *

from .core import *

from common import MyFunctions, waitforcomponent
from common.checks import is_admin
from common.localization import getname, localize

"""

Trash Extension

진짜 쓰잘데기 없는 기능들 모음 예를 들면 고양이 사진 보내기라던가...

"""


class Trash(Extension):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @slash_command(name=LocalisedName(english_us="owner", korean="니주인"), description=LocalisedDesc(english_us="who is your master", korean="너의 주인은 누구니"))
    async def owner(self, ctx: SlashContext):
        await ctx.send("저의 주인님은 전지전능하고 위대하신 <@!366269351080361995> 님이십니다!")


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    Trash(bot)


def teardown():
    # functions_.remove()
    pass
