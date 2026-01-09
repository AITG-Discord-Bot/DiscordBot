from interactions import listen
from interactions.api.events import MemberRemove
from ..utils import process_nick
from Extensions.Server.model import ServerBase
from API.features.warthunder import warthunderAPI


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
    if server.clanname is None:
        return
    vacations = await warthunderAPI.clan.get_vacation(server.clanname)
    nickname = None
    for vacation in vacations:
        nickname = vacation.member.nick
        if nickname == nick:
            break
    else:
        return

    await warthunderAPI.clan.delete_vacation(server.clanname, nickname)

    if server.botmessagechannel:
        _ = server.localizator
        await server.botmessagechannel.send(
            _("wt_vacation_member_removed").format(member.mention, nickname)
        )
    return
