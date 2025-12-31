from interactions.api.events import MemberAdd
from interactions import *
from ..model import ServerBase
from common.discordbot import safe_send


async def handle(event: MemberAdd):
    newmember = event.member
    bot = event.bot
    guild = event.guild
    server = ServerBase(bot, guild.id)
    await server.get()
    if server.welcomemessage:
        msg = server.welcomemessage
        msg = msg.replace(";user;", newmember.mention)
        systemchannel = server.server.system_channel
        await safe_send(bot, systemchannel, msg)
