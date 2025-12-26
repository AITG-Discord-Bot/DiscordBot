from interactions import listen
from interactions.api.events import MemberRemove
from ..utils import process_nick
from common import apirequest
from Extensions.Server.model import ServerBase


async def on_member_remove(event: MemberRemove):
    bot = event.bot
    if not bot.is_ready:
        return
    guild = event.guild
    member = event.member
    nick = member.display_name
    nick = process_nick(nick)
    server = ServerBase(bot=bot, serverid=guild.id)
    await server.get()
    vacations: list[dict] = await apirequest(
        f"/warthunder/clan/{server.clanname}/vacation", method="GET"
    )
    nickname = None
    for vacation in vacations:
        nickname = vacation["member"]["nick"]
        if nickname == nick:
            break
    else:
        return

    await apirequest(
        f"/warthunder/clan/{server.clanname}/vacation/{nick}", method="DELETE"
    )

    if server.botmessagechannel:
        _ = server.localizator
        await server.botmessagechannel.send(
            _("wt_vacation_member_removed").format(member.mention, nickname)
        )
    return
