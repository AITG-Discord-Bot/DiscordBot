from random import randint

from interactions import *
from interactions.ext.paginators import Paginator

from API import APIRequestError
from common.discordbot import safe_send
from common.localization import (
    language_utc_offsets,
    default_locale,
)
from . import utils
from Extensions.Server.model import ServerBase
from API.features.warthunder import warthunderAPI, request

async def check_clanmate_core(ctx: SlashContext, _):
    await ctx.defer(ephemeral=True)
    server = await utils.check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    web_members = await warthunderAPI.clan.get_members(server.clanname)
    web_names = [m.nick for m in web_members]
    discord_members = utils.get_discord_clanmates(ctx.guild, server.clanmaterole)

    matched: list[Member] = []
    for m in discord_members:
        nick = utils.process_nick(m.display_name)
        if nick in web_names:
            web_names.remove(nick)
            matched.append(m)

    who_is_this: list[Member] = [m for m in discord_members if m not in matched]

    embed = Embed(title=_("wt_clanmate_check_results"), color=randint(0, 0xFFFFFF))
    if matched:
        embed.add_field(
            name=_("wt_clanmate_who_is_this"),
            value=", ".join([m.mention for m in who_is_this]) or "X",
            inline=False,
        )
    if web_names:
        embed.add_field(
            name=_("wt_clanmate_not_found"),
            value="```\n" + ", ".join(web_names) + "\n```",
            inline=False,
        )
    if not matched and not web_names:
        embed.description = _("wt_clanmate_no_clanmates")
    embed = utils.create_footer(web_members, embed, _)
    await ctx.send(embeds=embed, ephemeral=True)


async def check_activity_core(
    ctx: SlashContext,
    _,
    threshold: int,
    use_personalrating: bool,
    ephemeral: bool,
):
    server = await utils.check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    locale = ctx.locale or "en"
    page_size = 30

    web_members = await warthunderAPI.clan.get_members(server.clanname)
    web_members = sorted(web_members, key=lambda x: -int(x.activity))
    filtered = [m for m in web_members if int(m.activity) <= threshold]

    if not filtered:
        embed = Embed(
            title=_("wt_clanmate_activity_check_results"),
            description=_("wt_clanmate_no_active_members"),
            color=randint(0, 0xFFFFFF),
        )
        embed = utils.create_footer(web_members, embed, _)
        await ctx.send(embeds=embed, ephemeral=ephemeral)
        return

    nicks = [m["nick"] for m in filtered]
    if use_personalrating:
        acts = [str(m["rating"]) for m in filtered]
    else:
        acts = [str(m["activity"]) for m in filtered]
    vacations = [
        (
            "~" + utils.to_local(m["vacation"][0]["enddate"], locale)
            if m.get("vacation")
            else "X"
        )
        for m in filtered
    ]

    pages = []
    for i in range(0, len(nicks), page_size):
        start = i + 1
        end = min(i + page_size, len(nicks))
        embed = Embed(
            title=_("wt_clanmate_activity_check_results").format(start, end),
            color=randint(0, 0xFFFFFF),
        )
        embed.add_field(
            name=_("common_nick"),
            value="```\n" + "\n".join(nicks[i : i + page_size]) + "```",
            inline=True,
        )
        embed.add_field(
            name=_("wt_activity"),
            value="```\n" + "\n".join(acts[i : i + page_size]) + "```",
            inline=True,
        )
        embed.add_field(
            name=_("wt_vacation"),
            value="```\n" + "\n".join(vacations[i : i + page_size]) + "```",
            inline=True,
        )
        embed = utils.create_footer(web_members, embed, _)
        pages.append(embed)

    if len(pages) == 1:
        await ctx.send(embeds=pages[0], ephemeral=ephemeral)
        return

    paginator = Paginator.create_from_embeds(ctx.bot, *pages, timeout=120)
    paginator.show_select_menu = True
    await paginator.send(ctx, ephemeral=ephemeral)


async def add_vacation_core(ctx: SlashContext, _, options_member: Member | None):
    server = await utils.check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    if not await utils.check_users(ctx, server, options_member, _):
        return

    target = options_member if options_member else ctx.author
    nick = utils.process_nick(target.display_name)
    try:
        member = await warthunderAPI.clan.get_member(server.clanname, nick)
    except APIRequestError as e:
        if e.status == 404:
            await ctx.send(
                _("wt_clanmate_you_not_in_clan").format(
                    nick=nick, clanname=server.clanname
                ),
                ephemeral=True,
            )
            return
        raise

    locale = ctx.locale or default_locale
    now_str = (
        utils.datetime.now(utils.UTC)
        + utils.timedelta(hours=utils.language_utc_offsets[locale])
    ).strftime("%Y-%m-%d")

    modal = Modal(
        ShortText(
            label=_("wt_add_vacation_modal_reason"),
            placeholder=_("wt_add_vacation_modal_reason_placeholder"),
            required=True,
            max_length=100,
            custom_id="vacation_reason",
        ),
        ShortText(
            label=_("wt_add_vacation_modal_enddate"),
            value=now_str,
            required=True,
            max_length=10,
            min_length=10,
            custom_id="vacation_enddate",
        ),
        title=_("wt_add_vacation_modal_title"),
    )
    await ctx.send_modal(modal=modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal, timeout=300)
    await modal_ctx.defer(ephemeral=True)

    reason = modal_ctx.responses["vacation_reason"]
    enddate_str = modal_ctx.responses["vacation_enddate"]
    enddate = utils.parse_date(enddate_str)

    if not enddate:
        await modal_ctx.send(
            _("wt_add_vacation_invalid_date").format(date=enddate_str), ephemeral=True
        )
        return
    if enddate < utils.parse_date(now_str):
        await modal_ctx.send(
            _("wt_add_vacation_date_in_past").format(date=enddate_str), ephemeral=True
        )
        return

    # 23:59:59 고정 후 UTC 보정
    enddate = enddate.replace(hour=23, minute=59, second=59)
    enddate = enddate + utils.timedelta(hours=-utils.language_utc_offsets[locale])

    dto = request.clan.ThunderClanVacationDTO(memberidx=member.idx, reason=reason, enddate=enddate)
    await warthunderAPI.clan.add_vacation(dto)
    await modal_ctx.send(_("wt_add_vacation_success"), ephemeral=True)

    if server.botmessagechannel:
        local_end = utils.to_local(enddate.isoformat(), locale)
        await server.botmessagechannel.send(
            _("wt_add_vacation_announcement").format(nick, local_end, reason)
        )


async def view_vacation_core(ctx: SlashContext, _, ephemeral: bool):
    server = await utils.check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return

    vacations = await warthunderAPI.clan.get_vacation(server.clanname)
    members = utils.get_discord_clanmates(ctx.guild, server.clanmaterole)

    display_names = {}
    for v in vacations:
        nick = v.member.nick
        display_names[nick] = "X"
        for m in members:
            if utils.process_nick(m.display_name) == nick:
                display_names[nick] = m.mention
                break

    vacations = sorted(vacations, key=lambda x: (x.enddate, x.member.nick))
    if not vacations:
        await ctx.send(_("wt_view_vacation_no_vacations"), ephemeral=ephemeral)
        return

    msg = "\n".join(
        f"{display_names[v.member.nick]} `{v.member.nick}` - {utils.to_local(v.enddate.isoformat(), ctx.locale or 'en')} - {v.reason}"
        for v in vacations
    )
    embed = Embed(
        title=_("wt_view_vacation_list"), description=msg, color=randint(0, 0xFFFFFF)
    )
    await ctx.send(embeds=embed, ephemeral=ephemeral)


async def remove_vacation_core(ctx: SlashContext, _, options_member: Member | None):
    server = await utils.check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    if not await utils.check_users(ctx, server, options_member, _):
        return

    target = options_member if options_member else ctx.author
    nick = utils.process_nick(target.display_name)
    try:
        await warthunderAPI.clan.delete_vacation(server.clanname, nick)
    except APIRequestError:
        await ctx.send(
            _("wt_remove_vacation_no_vacation").format(nick=nick), ephemeral=True
        )


async def send_latest_news(ctx: SlashContext, _):
    guild = ctx.guild
    bot = ctx.bot
    server = ServerBase(bot, guild.id)
    await server.get()
    lang = server.newslang
    newschannel = server.subnews
    if not newschannel:
        await ctx.send(_("wt_send_latest_news_no_newschannel"), ephemeral=True)
        return
    try:
        res = await warthunderAPI.news.get_latest(lang)
    except APIRequestError as e:
        if int(e.error_code) == 404:
            await ctx.send(_("wt_send_latest_news_no_news"), ephemeral=True)
            return
        else:
            raise e
    embed = utils.create_news_embed(res, _)
    await safe_send(bot, newschannel, embeds=[embed])
