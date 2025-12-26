from interactions import Client, Member

from Extensions.WarThunder.utils import to_local, process_nick
from common.localization import default_locale, localizator
from Extensions.Server.model import ServerBase
from common import safe_send, safe_dm
from .utils import create_news_embed


async def notify_vacation_end(bot: Client, params):
    for vacation in params:
        serverid = vacation["serverid"]
        server = ServerBase(bot, serverid)
        await server.get()
        if not server:
            continue
        if not server.clanmaterole:
            continue
        _ = server.localizator
        clanname = vacation["clanname"]
        nick = vacation["nick"]
        reason = vacation["reason"]
        message = _("wt_vacation_ended_notification").format(nick, clanname, reason)
        user: Member | None = None
        for member in server.server.members:
            if (
                member.has_role(server.clanmaterole)
                and process_nick(member.display_name) == nick
            ):
                user = member
                break
        await safe_dm(user, message)
        await safe_send(bot, server.botmessagechannel, message)


async def send_news(bot: Client, params):
    serverids = params["serverids"]
    newsdata = params["news"]
    newscache = {}
    for serverid in serverids:
        server = ServerBase(bot, serverid)
        await server.get()
        if not server:
            continue
        server_locale = server.server.preferred_locale or default_locale
        for lang in newsdata:
            newslist = newsdata[lang]
            for news in newslist:
                key_ = (lang, news["title"], server_locale)
                if newscache.get(key_, None):
                    embed = newscache[key_]
                else:
                    localizer = server.localizator
                    embed = create_news_embed(news, localizer)
                    newscache[key_] = embed
                await safe_send(bot, server.subnews, embeds=[embed])
