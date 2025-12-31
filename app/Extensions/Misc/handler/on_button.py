import asyncio

from interactions import *
from common.discordbot import waitforcomponent
from common.guards import is_admin
from ..utils import decode_embed
from Extensions.Server.model import ServerBase

anytextchannels = [
    ChannelType.GUILD_TEXT,
    ChannelType.GUILD_NEWS,
    ChannelType.GUILD_NEWS_THREAD,
    ChannelType.GUILD_PUBLIC_THREAD,
    ChannelType.GUILD_PRIVATE_THREAD,
]


async def handle(ctx: ComponentContext, _):
    bot = ctx.bot
    ctx_message = ctx.message

    if ctx.custom_id == "submit_embed_url":
        modal = Modal(
            ParagraphText(
                label=_("misc_submit_embed_url_label"),
                custom_id="embed_json",
                placeholder=_("misc_submit_embed_url_label_placeholder"),
                required=True,
            ),
            title=_("misc_submit_embed_url_modal_title"),
        )
        await ctx.send_modal(modal=modal)
        modal_ctx: ModalContext = await bot.wait_for_modal(modal, timeout=300)
        embed_json = modal_ctx.responses["embed_json"]
        embed_json = decode_embed.decode_embed(embed_json)
        embed = Embed.from_dict(embed_json)
        channel_select = ChannelSelectMenu(
            channel_types=anytextchannels,
            placeholder=_("common_select_channel"),
        )
        msg = await modal_ctx.send(
            _("common_select_channel"), components=channel_select, ephemeral=True
        )
        used_ctx = await waitforcomponent(bot, ctx.author, msg, channel_select)
        if used_ctx is None:
            return
        channel: BaseChannel = used_ctx.values[0]
        msg: Message = await channel.send(embeds=embed)
        await used_ctx.send(
            _("misc_submit_embed_url_success").format(msg.jump_url), ephemeral=True
        )

    elif ctx.custom_id.startswith("ticket_create"):
        server = ServerBase(bot, int(ctx.guild.id), _)
        await server.get()
        modrole = server.modrole
        if modrole is None:
            return
        category = ctx.channel.category
        if category is None:
            await ctx.send("카테고리를 찾을 수 없습니다.", ephemeral=True)
            return
        author = ctx.author
        ticket_id = str(author.id)[-4:]
        allow_overrides = (
            Permissions.VIEW_CHANNEL
            | Permissions.SEND_MESSAGES
            | Permissions.EMBED_LINKS
            | Permissions.ATTACH_FILES
            | Permissions.ADD_REACTIONS
        )
        bot_overrides = allow_overrides | Permissions.MANAGE_CHANNELS
        permission_overwrites = []
        try:
            for role in ctx.guild.roles:
                if (
                    Permissions.VIEW_CHANNEL
                    in ctx_message.channel.permissions_for(role)
                    and role != modrole
                ):
                    permission_overwrites.append(
                        PermissionOverwrite(
                            id=role.id,
                            type=OverwriteType.ROLE,
                            deny=Permissions.VIEW_CHANNEL,
                        )
                    )
            permission_overwrites.append(
                PermissionOverwrite(
                    id=ctx.guild.default_role.id,
                    type=OverwriteType.ROLE,
                    deny=Permissions.VIEW_CHANNEL,
                )
            )
            permission_overwrites.append(
                PermissionOverwrite(
                    id=modrole.id, type=OverwriteType.ROLE, allow=allow_overrides
                )
            )
            permission_overwrites.append(
                PermissionOverwrite(
                    id=author.id, type=OverwriteType.MEMBER, allow=allow_overrides
                )
            )
            permission_overwrites.append(
                PermissionOverwrite(
                    id=bot.user.id, type=OverwriteType.MEMBER, allow=bot_overrides
                )
            )
            ticket = await category.create_text_channel(
                f"ticket-{ticket_id}", permission_overwrites=permission_overwrites
            )
            component = Button(
                label=_("misc_ticket_close"),
                custom_id=f"ticket_close_{author.id}",
                style=4,
            )
            message = await ticket.send(
                content=_("misc_ticket_created").format(author.mention, author.mention),
                components=[component],
            )
            await message.pin()
        except Exception:
            await ctx.send(
                _("misc_ticket_create_error"),
                ephemeral=True,
                delete_after=30,
            )
            return
        await ctx.send(
            _("misc_ticket_created_1").format(ticket.mention),
            ephemeral=True,
            delete_after=30,
        )

    elif ctx.custom_id.startswith("ticket_close_"):
        admin = await is_admin(ctx)
        ticket = ctx.channel
        ticket_author = await bot.fetch_user(int(ctx.custom_id.split("_")[-1]))
        if ticket_author is None:
            await ctx.send(_("misc_ticket_cannot_close"), ephemeral=True)
            return
        if ticket_author.id != ctx.author.id:
            await ctx.send(_("misc_ticket_not_allowed"), ephemeral=True)
            return
        component = ctx.message.components[0]
        component.disabled = True
        await ctx.message.edit(components=[component])
        if admin and ctx.author.id != ticket_author.id:
            await ticket.set_permission(ticket_author, send_messages=False)
            component = []
            if "forever" not in ctx.custom_id:
                component.append(
                    Button(
                        label=_("misc_ticket_reopen"),
                        custom_id=f"ticket_reopen_{ticket_author.id}",
                        style=1,
                    )
                )
            await ctx.send(
                _("misc_ticket_closed").format(ctx.author.mention),
                components=component,
                ephemeral=False,
            )
            return
        component = Button(label=_("common_delete_channel"), custom_id="ticket_delete", style=4)
        await ctx.send(
            _("misc_ticket_closed_1").format(ticket_author.mention),
            components=[component],
            ephemeral=False,
        )
        await asyncio.sleep(5)
        await ticket.set_permission(
            ticket_author, view_channel=False, send_messages=False
        )
