import asyncio
from datetime import datetime, UTC, timedelta
from json import loads

import interactions.api.events as Events
from interactions import (
    Extension,
    Client,
    SlashCommand,
    SlashContext,
    Modal,
    ShortText,
    ParagraphText,
    slash_option,
    OptionType,
    ModalContext,
    ActionRow,
    RoleSelectMenu,
    Button,
    ButtonStyle,
    listen,
    ChannelSelectMenu,
    ChannelType,
    ComponentType,
    UserSelectMenu,
    ComponentContext,
    Guild,
)
from interactions.api.events import Component
from interactions.models.discord.user import Member

from common import MyFunctions, var, apirequest, RateLimiter
from common.localization import (
    getname,
    getdesc,
    localize,
    language_utc_offsets,
    localizator,
)
from .model import ClanwarBase, PARTYACTIONS


notify_clanwar_url = "clanwar_notify"
clanwarbase = SlashCommand(name=getname("clanwar.command.base"))


def partyid():
    def wrapper(func):
        return slash_option(
            name=getname("clanwar.option.partyid"),
            description=getdesc("clanwar.option.partyid.desc"),
            opt_type=OptionType.STRING,
            required=True,
            autocomplete=True,
        )(func)

    return wrapper


class Clanwar(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
        self.ratelimiter = RateLimiter(max_calls=2, period=60)

    @clanwarbase.subcommand(
        sub_cmd_name=getname("clanwar.command.add"),
        sub_cmd_description=getdesc("clanwar.command.add.desc"),
    )
    @localize()
    async def add_clanwar(self, ctx: SlashContext, _):
        locale = ctx.locale
        utc_offset = language_utc_offsets.get(locale, 0)
        now = datetime.now(UTC)
        # clanwar opens at 14:00 UTC
        if now.hour >= 14:
            now = now + timedelta(days=1)
        now = now.replace(hour=14)
        now = now + timedelta(hours=utc_offset)
        now = now.replace(minute=0, second=0, microsecond=0)
        now = now.strftime("%Y-%m-%d %H:00")
        my_modal = Modal(
            ShortText(
                label=_("clanwar.modal.add.time").format(str(utc_offset)),
                custom_id="partytime",
                placeholder="YYYY-MM-DD HH:MM",
                value=now,
                required=True,
            ),
            ParagraphText(
                label=_("clanwar.modal.add.desc"),
                custom_id="partydesc",
                placeholder=_("clanwar.modal.add.desc.placeholder"),
                required=False,
            ),
            ShortText(
                label=_("clanwar.modal.add.BR"),
                custom_id="partybr",
                placeholder=_("clanwar.modal.add.BR.placeholder"),
                required=True,
            ),
            title=_("clanwar.modal.add.title"),
        )
        await ctx.send_modal(modal=my_modal)
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(
            modal=my_modal, timeout=300
        )
        await modal_ctx.defer()
        partytime = modal_ctx.responses["partytime"]
        partytime = convert_time(partytime, utc_offset)
        if partytime is None:
            await ctx.send(_("clanwar.wrong_timeformat"), ephemeral=True)
            return
        partydesc = modal_ctx.responses["partydesc"]
        partygame = modal_ctx.responses["partybr"]
        row1 = ActionRow(
            RoleSelectMenu(
                placeholder=_("clanwar.mention_placeholder"), min_values=1, max_values=1
            )
        )
        row2 = ActionRow(
            Button(label=_("clanwar.no_mention_button"), style=ButtonStyle.RED)
        )
        component_msg = await modal_ctx.send(
            _("clanwar.select_mention"),
            components=[row1, row2],
            ephemeral=True,
            delete_after=60,
        )
        component_rsp: Component = await ctx.bot.wait_for_component(
            components=[row1, row2], timeout=60
        )
        component_ctx = component_rsp.ctx
        role = None
        if component_ctx.component_type == 6:
            role = component_ctx.values[0]
        await component_msg.delete()
        party = ClanwarBase(_, bot=self.bot)
        await party.create_party(ctx, partydesc, partygame, partytime, role)

    @listen(Events.Component)
    @localize()
    async def on_component(self, ctx: ComponentContext, _):
        if ctx.component_type == ComponentType.BUTTON:
            return await self.on_button(ctx, _)
        elif ctx.component_type == ComponentType.STRING_SELECT:
            return await self.on_string_select(ctx, _)
        elif ctx.component_type == ComponentType.CHANNEL_SELECT:
            return await self.on_channel_select(ctx, _)
        elif ctx.component_type == ComponentType.USER_SELECT:
            return await self.on_user_select(ctx, _)
        return None

    async def on_button(self, ctx: ComponentContext, _):
        author = ctx.author
        message = ctx.message
        custom_id = ctx.custom_id
        author_id = int(author.id)
        if custom_id.endswith("party"):
            if not self.ratelimiter.get(author_id):
                await ctx.send(
                    _("common.ratelimit").format(1, 2), ephemeral=True, delete_after=5
                )
                return

            party = ClanwarBase(_, ctx=ctx)
            await party.get_party(message=message)
            if author.id == party.owner.id:
                await ctx.send(
                    _("clanwar.no_owner_area"), ephemeral=True, delete_after=5
                )
                return

            if custom_id == "exit_party":
                await party.remove_people(author)
                await party.edit_embed(save=False)
                await ctx.send(_("clanwar.leave"), ephemeral=True, delete_after=5)

            if author.id in party.participant + party.primarywaiter + party.waiter:
                await ctx.send(
                    _("clanwar.leave_first"),
                    ephemeral=True,
                    delete_after=5,
                )
                return

            if custom_id == "join_party":
                result = await party.add_people(author)
                await party.edit_embed(save=False)
                if result == PARTYACTIONS.PRIMARY_PARTY:
                    await ctx.send(
                        _("clanwar.wait_party"), ephemeral=True, delete_after=5
                    )
                else:
                    await ctx.send(
                        _("clanwar.join_party"), ephemeral=True, delete_after=5
                    )

            elif custom_id == "wait_party":
                await party.add_people(author, wait=True)
                await party.edit_embed(save=False)
                await ctx.send(
                    _("clanwar.pending_party"), ephemeral=True, delete_after=5
                )

    async def on_string_select(self, ctx, _):
        author = ctx.author
        message = ctx.message
        custom_id = ctx.custom_id
        party = ClanwarBase(_, ctx=ctx)
        await party.get_party(message=message)
        if author.id != party.owner.id and author.id not in var.dev:
            await ctx.send(_("clanwar.only_owner_area"), ephemeral=True, delete_after=5)
            return
        if custom_id.endswith("party"):
            value = ctx.values[0]
            match value:
                case "edit_voicechannel":
                    select = ChannelSelectMenu(
                        custom_id=f"party_voicechannel_{party.partyid}",
                        placeholder=_("common.select_voicechannel"),
                        channel_types=[ChannelType.GUILD_VOICE],
                    )
                    await ctx.send(
                        _("common.select_channel"),
                        components=[ActionRow(select)],
                        ephemeral=True,
                        delete_after=60,
                    )
                    return
                case "add_thread":
                    if await party.add_thread():
                        await ctx.send(
                            _("clanwar.thread_added"), ephemeral=True, delete_after=5
                        )
                    else:
                        await ctx.send(
                            _("clanwar.thread_exist"), ephemeral=True, delete_after=5
                        )
                    return
                case "delete_thread":
                    if await party.del_thread():
                        await ctx.send(
                            _("clanwar.thread_deleted"), ephemeral=True, delete_after=5
                        )
                    else:
                        await ctx.send(
                            _("clanwar.no_thread"), ephemeral=True, delete_after=5
                        )
                    return
                case "delete":
                    await party.delete()
                    await ctx.send(_("clanwar.deleted"), ephemeral=True, delete_after=5)
                    return
                case "end":
                    await party.end_party()
                    await ctx.send(_("clanwar.ended"), ephemeral=True, delete_after=5)
                    return

                case "start":
                    await party.start_party()
                    await ctx.send(_("clanwar.started"), ephemeral=True, delete_after=5)
                    return

                case "changeowner":
                    select = UserSelectMenu(
                        custom_id=f"party_changeowner_{party.partyid}",
                        placeholder=_("clanwar.select_owner"),
                    )
                    await ctx.send(
                        _("clanwar.select_owner"),
                        components=[ActionRow(select)],
                        ephemeral=True,
                        delete_after=60,
                    )
                    return

    async def on_channel_select(self, ctx, _):
        author = ctx.author
        custom_id = ctx.custom_id
        if custom_id.startswith("party_voicechannel"):
            party_id = custom_id.split("_")[2]
            party = ClanwarBase(_, bot=self.bot)
            await party.get_party(partyid=party_id)
            if author.id != party.owner.id and author.id not in var.dev:
                await ctx.send(
                    _("clanwar.only_owner_area"), ephemeral=True, delete_after=5
                )
                return
            voicechannel = ctx.values[0]
            url = f"https://discord.com/channels/{ctx.guild.id}/{voicechannel.id}"
            await ctx.send(
                _("clanwar.voicechannel_set").format(url),
                ephemeral=True,
                delete_after=5,
            )
            party.set_voicechannel(voicechannel)
            await party.edit_embed()
            # from here

    async def on_user_select(self, ctx, _):
        author = ctx.author
        custom_id = ctx.custom_id
        if custom_id.startswith("party_changeowner"):
            party_id = custom_id.split("_")[2]
            party = ClanwarBase(_, bot=self.bot)
            await party.get_party(partyid=party_id)
            if author.id != party.owner.id and author.id not in var.dev:
                await ctx.send(
                    _("clanwar.only_owner_area"), ephemeral=True, delete_after=5
                )
                return
            newowner = ctx.values[0]
            newowner = await ctx.guild.fetch_member(newowner)
            await party.change_owner(newowner)
            await ctx.send(_("clanwar.owner_changed"), ephemeral=True, delete_after=5)

    @listen(Events.MemberRemove, delay_until_ready=True)
    async def on_guild_left(self, event):
        if not self.bot.is_ready:
            return
        server: Guild = event.guild
        user: Member = event.member
        results = await apirequest(
            f"/clanwar/server/{server.id}/people/{user.id}", method="GET"
        )
        for result in results:
            clanwar = ClanwarBase(bot=self.bot)
            await clanwar.get_party(partyid=result.get("idx"))
            await clanwar.remove_people(user)
            await clanwar.edit_embed(save=False)


def convert_time(timestr, timeoffset):
    """Convert time to UTC"""
    try:
        for timeformat in [
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M",
            "%d %b %Y %H:%M",
            "%a %d %b %Y %H:%M",
            "%A %d %b %Y %H:%M",
            "%m/%d/%Y %H:%M",
        ]:
            partytime = datetime.strptime(timestr, timeformat)
            partytime = partytime + timedelta(hours=-timeoffset)
            break
    except ValueError:
        return None
    return partytime.strftime("%Y-%m-%d %H:%M")


async def notify_clanwar(bot: Client, params):
    for idx in params:
        clanwar = ClanwarBase(bot=bot)
        await clanwar.get_party(partyid=idx)
        await clanwar.notify()


functions_: MyFunctions = None


def setup(bot: Client, functions: MyFunctions):
    global functions_
    functions_ = functions
    functions_.set(notify_clanwar_url, notify_clanwar)
    Clanwar(bot)


def teardown():
    functions_.remove(notify_clanwar_url)
