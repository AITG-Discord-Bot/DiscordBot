from interactions import Client, Member

from Extensions.WarThunder.utils import to_local, process_nick
from common.localization import default_locale, localizator
from Extensions.Server.model import ServerBase


async def notify_vacation_end(bot: Client, params):
    for vacation in params:
        serverid = vacation["serverid"]
        clanmateroleid = vacation["clanmaterole"]
        server = ServerBase(bot, serverid)
        await server.get()
        if not server:
            continue
        clanmaterole = await server.server.fetch_role(clanmateroleid)
        if not clanmaterole:
            continue
        locale = server.server.preferred_locale or default_locale
        _ = localizator(locale)

        clanname = vacation["clanname"]
        nick = vacation["nick"]
        # enddate = to_local(vacation["enddate"], locale)
        reason = vacation["reason"]

        message = _("wt_vacation_ended_notification").format(nick, clanname, reason)

        user: Member | None = None
        for member in server.server.members:
            if (
                member.has_role(clanmaterole)
                and process_nick(member.display_name) == nick
            ):
                user = member
                break
        if user:
            try:
                await user.send(message)
            except:
                pass
        if server.botmessagechannel:
            try:
                await server.botmessagechannel.send(message)
            except:
                pass
