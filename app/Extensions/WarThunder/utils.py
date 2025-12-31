import re
from datetime import datetime, timedelta, UTC
from random import randint
from typing import Optional

from interactions import Guild, Role, Member, Embed, SlashContext

from Extensions.Server.model import ServerBase
from common.core import var
from common.localization import language_utc_offsets
from API.features.warthunder import response


def get_discord_clanmates(guild: Guild, role: Role) -> list[Member]:
    return [m for m in guild.members if m.has_role(role)]


def process_nick(nick: str) -> str:
    nick = re.sub(r"\(.*?\)", "", nick)
    nick = re.sub(r"\[.*?\]", "", nick)
    return nick.strip()


def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def to_local(dt_str: str, locale: str) -> str:
    dt = datetime.fromisoformat(dt_str)
    dt = dt + timedelta(hours=language_utc_offsets.get(locale, 0))
    return dt.strftime("%Y-%m-%d")


def create_footer(web_members: list[dict], embed: Embed, _) -> Embed:
    updatedat = web_members[0]["updated_at"] if web_members else None
    if updatedat:
        now = datetime.now(UTC)
        updatedat_dt = datetime.fromisoformat(updatedat).replace(tzinfo=UTC)
        diff = now - updatedat_dt
        hours = diff.days * 24 + diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        embed.set_footer(text=_("wt_clanmate_data_updated_at").format(hours, minutes))
    return embed


async def check_prerequisites(ctx: SlashContext, serverid: int, _):
    server = ServerBase(ctx.bot, serverid, _)
    await server.get()
    if not server.clanname:
        await ctx.send(_("wt_no_clan_set"), ephemeral=True)
        return None
    if not server.clanmaterole:
        await ctx.send(_("wt_no_clanmate_role_set"), ephemeral=True)
        return None
    return server


async def check_users(
    ctx: SlashContext, server: ServerBase, options_member: Member | None, _
) -> bool:
    if not ctx.author.has_role(server.clanmaterole):
        await ctx.send(
            _("wt_clanmate_you_not_clanmate").format(clanname=server.clanname),
            ephemeral=True,
        )
        return False
    if options_member and not ctx.author.has_role(server.modrole):
        await ctx.send(_("wt_clanmate_only_mod_can_set_others"), ephemeral=True)
        return False
    return True


def create_news_embed(res: response.news.NewsDTO, _) -> Embed:
    title = res.title
    link = res.link
    content = res.content
    time = res.time
    time = time.strftime("%Y-%m-%d %H:%M")
    poster = res.poster
    embed = Embed(title=title, description=content, color=randint(0, 0xFFFFFF))
    embed.set_image(url=poster)
    baseurl = var.warthunderbaseurl[:-1]
    embed.url = baseurl + link
    embed.set_author(
        name="워썬더 소식!", icon_url="https://warthunder.com/i/opengraph-wt.jpg"
    )
    embed.set_footer(text=f"가장 최신 뉴스: {time}UTC")
    return embed
