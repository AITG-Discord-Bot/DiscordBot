from interactions import *
from .model import ServerBase
from . import utils


async def set_mod_role(ctx: SlashContext, _, options_role):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.update(modrole=options_role)
    await ctx.send(
        _("server_setmodrole_success").format(options_role.mention), ephemeral=True
    )


async def view_settings(ctx: SlashContext, _, ephemeral: bool = True):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.get()
    embed = await server.create_embed()
    await ctx.send(embeds=[embed], ephemeral=ephemeral)


async def set_bot_message_channel(ctx: SlashContext, _, options_textchannel: GuildText):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.update(botmessagechannel=options_textchannel)
    await ctx.send(
        _("server_setbotmessagechannel_success").format(options_textchannel.mention),
        ephemeral=True,
    )


async def set_clanmate_role(ctx: SlashContext, _, options_role):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.update(clanmaterole=options_role)
    await ctx.send(
        _("server_setclanmaterole_success").format(options_role.mention),
        ephemeral=True,
    )


async def set_news_channel(ctx: SlashContext, _, options_textchannel: GuildText):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.update(subnews=options_textchannel)
    await ctx.send(
        _("server_setnewschannel_success").format(options_textchannel.mention),
        ephemeral=True,
    )


async def set_news_language(ctx: SlashContext, _, lang: str):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.update(newslang=lang)
    await ctx.send(
        _("server_setnewslanguage_success").format(lang),
        ephemeral=True,
    )


# async def set_link_role_(ctx: SlashContext, _, options_role):
#         serverid = int(ctx.guild_id)
#         server = ServerBase(ctx.bot, serverid, _)
#         await server.update(linkrole=options_role)
#         await ctx.send(
#             _("server_setlinkrole_success").format(options_role.mention),
#             ephemeral=True,
#         )


async def set_clan_name(ctx: SlashContext, _):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    modal = Modal(
        ShortText(
            label=_("server_clanname_modal_label"),
            placeholder=_("server_clanname_modal_placeholder"),
            custom_id="clanname",
            max_length=100,
            required=True,
        ),
        title=_("server_clanname_modal_title"),
    )
    await ctx.send_modal(modal=modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal=modal, timeout=300)
    await modal_ctx.defer(ephemeral=True)
    clanname = modal_ctx.responses["clanname"]
    existing = await utils.get_clan_names()
    if clanname in existing:
        await modal_ctx.send(
            _("server_clanname_modal_error_exists").format(clanname),
            ephemeral=True,
        )
        return
    valid = await utils.verify_clanname(clanname)
    if not valid:
        await modal_ctx.send(
            _("server_clanname_modal_error_invalid").format(clanname),
            ephemeral=True,
        )
        return
    await server.update(clanname=clanname)
    await modal_ctx.send(
        _("server_clanname_modal_success").format(clanname), ephemeral=True
    )


async def set_welcome_message(ctx: ContextMenuContext, _):
    serverid = int(ctx.guild_id)
    server = ServerBase(ctx.bot, serverid, _)
    await server.get()
    message: Message = ctx.target
    await server.update(welcomemessage=message.content)
    await ctx.send(_("server_app_set_welcome_message_success"), ephemeral=True)


async def set_welcomemessage_helper(ctx: SlashContext, _):
    imgurl = "https://raw.githubusercontent.com/AITG-Discord-Bot/AITG-Web/refs/heads/main/imgs/setwelcommessage.png"
    await ctx.send(
        _("server_setwelcomemessage_helper_msg") + "\n\n" + imgurl, ephemeral=True
    )
