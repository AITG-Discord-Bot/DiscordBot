from random import randint

from aiohttp import ClientResponseError
from interactions import Modal, ShortText, ModalContext
from interactions.ext.paginators import Paginator

from .utils import *
from common import apirequest
from common.localization import (
    language_utc_offsets,
    default_locale,
)


async def check_clanmate_core(ctx: SlashContext, _):
    await ctx.defer(ephemeral=True)
    server = await check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    web_members: list[dict] = await apirequest(
        "/warthunder/clan/members", params={"clanname": server.clanname}
    )
    web_names = [m["nick"] for m in web_members]
    discord_members = get_discord_clanmates(ctx.guild, server.clanmaterole)

    matched: list[Member] = []
    for m in discord_members:
        nick = process_nick(m.display_name)
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
    embed = create_footer(web_members, embed, _)
    await ctx.send(embeds=embed, ephemeral=True)


async def check_activity_core(ctx: SlashContext, _, threshold: int, ephemeral: bool):
    server = await check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    locale = ctx.locale or "en"
    page_size = 30

    web_members: list[dict] = await apirequest(
        "/warthunder/clan/members", params={"clanname": server.clanname}
    )
    web_members = sorted(web_members, key=lambda x: -int(x["activity"]))
    filtered = [m for m in web_members if int(m["activity"]) < threshold]

    if not filtered:
        embed = Embed(
            title=_("wt_clanmate_activity_check_results"),
            description=_("wt_clanmate_no_active_members"),
            color=randint(0, 0xFFFFFF),
        )
        embed = create_footer(web_members, embed, _)
        await ctx.send(embeds=embed, ephemeral=ephemeral)
        return

    nicks = [m["nick"] for m in filtered]
    acts = [str(m["activity"]) for m in filtered]
    vacations = [
        (
            "~" + to_local(m["vacation"][0]["enddate"], locale)
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
            value="```" + "\n".join(nicks[i : i + page_size]) + "```",
            inline=True,
        )
        embed.add_field(
            name=_("wt_activity"),
            value="```" + "\n".join(acts[i : i + page_size]) + "```",
            inline=True,
        )
        embed.add_field(
            name=_("wt_vacation"),
            value="```" + "\n".join(vacations[i : i + page_size]) + "```",
            inline=True,
        )
        embed = create_footer(web_members, embed, _)
        pages.append(embed)

    if len(pages) == 1:
        await ctx.send(embeds=pages[0], ephemeral=ephemeral)
        return

    paginator = Paginator.create_from_embeds(ctx.bot, *pages, timeout=120)
    paginator.show_select_menu = True
    await paginator.send(ctx, ephemeral=ephemeral)


async def add_vacation_core(ctx: SlashContext, _, options_member: Member | None):
    server = await check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    if not await check_users(ctx, server, options_member, _):
        return

    target = options_member if options_member else ctx.author
    nick = process_nick(target.display_name)
    try:
        member = await apirequest(
            f"/warthunder/clan/{server.clanname}/member/{nick}", method="GET"
        )
    except ClientResponseError as e:
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
        datetime.now(UTC) + timedelta(hours=language_utc_offsets[locale])
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
    enddate = parse_date(enddate_str)

    if not enddate:
        await modal_ctx.send(
            _("wt_add_vacation_invalid_date").format(date=enddate_str), ephemeral=True
        )
        return
    if enddate < parse_date(now_str):
        await modal_ctx.send(
            _("wt_add_vacation_date_in_past").format(date=enddate_str), ephemeral=True
        )
        return

    # 23:59:59 고정 후 UTC 보정
    enddate = enddate.replace(hour=23, minute=59, second=59)
    enddate = enddate + timedelta(hours=-language_utc_offsets[locale])

    payload = {
        "memberidx": member["idx"],
        "reason": reason,
        "enddate": enddate.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    await apirequest("/warthunder/clan/vacation", method="POST", json=payload)
    await modal_ctx.send(_("wt_add_vacation_success"), ephemeral=True)

    if server.botmessagechannel:
        local_end = to_local(payload["enddate"], locale)
        await server.botmessagechannel.send(
            _("wt_add_vacation_announcement").format(nick, local_end, reason)
        )


async def view_vacation_core(ctx: SlashContext, _):
    server = await check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return

    vacations: list[dict] = await apirequest(
        f"/warthunder/clan/{server.clanname}/vacation", method="GET"
    )
    members = get_discord_clanmates(ctx.guild, server.clanmaterole)

    for v in vacations:
        nick = v["member"]["nick"]
        v["member"]["discord"] = "X"
        for m in members:
            if process_nick(m.display_name) == nick:
                v["member"]["discord"] = m.mention
                break

    vacations = sorted(vacations, key=lambda x: (x["enddate"], x["member"]["nick"]))
    if not vacations:
        await ctx.send(_("wt_view_vacation_no_vacations"), ephemeral=True)
        return

    msg = "\n".join(
        f"{v['member']['discord']} `{v['member']['nick']}` - {to_local(v['enddate'], ctx.locale or 'en')} - {v['reason']}"
        for v in vacations
    )
    embed = Embed(
        title=_("wt_view_vacation_list"), description=msg, color=randint(0, 0xFFFFFF)
    )
    await ctx.send(embeds=embed, ephemeral=True)


async def remove_vacation_core(ctx: SlashContext, _, options_member: Member | None):
    server = await check_prerequisites(ctx, int(ctx.guild_id), _)
    if not server:
        return
    if not await check_users(ctx, server, options_member, _):
        return

    target = options_member if options_member else ctx.author
    nick = process_nick(target.display_name)
    res = await apirequest(
        f"/warthunder/clan/{server.clanname}/vacation/{nick}", method="DELETE"
    )
    if res:
        await ctx.send(
            _("wt_remove_vacation_success").format(nick=nick), ephemeral=True
        )
    else:
        await ctx.send(
            _("wt_remove_vacation_no_vacation").format(nick=nick), ephemeral=True
        )
