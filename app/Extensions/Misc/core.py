from random import randint

from interactions import *

from Extensions.Server.model import ServerBase
from common import waitforcomponent, safe_send


async def send_to_channel(ctx: ContextMenuContext, _):
    message: Message = ctx.target
    channeltype = [ChannelType.GUILD_NEWS, ChannelType.GUILD_TEXT]
    component = ChannelSelectMenu(
        channel_types=channeltype, placeholder=_("common_select_channel")
    )
    channelselmsg = await ctx.send(
        _("common_select_channel"), components=[component], ephemeral=True
    )
    used_ctx = await waitforcomponent(ctx.bot, ctx.author, channelselmsg, component)
    if used_ctx is None:
        return
    channel: GuildText = used_ctx.values[0]
    try:
        await channel.send(
            message.content,
            embeds=message.embeds,
            allowed_mentions=AllowedMentions.all(),
        )
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                await channel.send(attachment.url)
        await used_ctx.edit_origin(
            content=_("app_sent_to_channel") + channel.mention, components=[]
        )
    except Exception as e:
        await used_ctx.edit_origin(
            content=_("app_send_to_channel_error") + "\n" + str(e),
            components=[],
        )


async def set_ticket(ctx: ContextMenuContext, _):
    message: Message = ctx.target
    bot: Client = ctx.bot
    emoji = PartialEmoji.from_str(":envelope_with_arrow:")
    my_modal = Modal(
        ShortText(
            label=_("set_ticket_button_label"),
            custom_id="button_label",
            placeholder=_("set_ticket_button_label_placeholder"),
            min_length=1,
            max_length=80,
        ),
        title="Input Button Label",
    )
    await ctx.send_modal(modal=my_modal)
    modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)
    button_label = modal_ctx.responses["button_label"]
    component = Button(
        label=f"{button_label}", custom_id="ticket_create", style=1, emoji=emoji
    )
    await safe_send(
        bot,
        message.channel,
        message.content,
        components=[component],
    )
    await modal_ctx.send(_("app_set_ticket_success"), ephemeral=True, delete_after=10)
    await ctx.send(_("app_set_ticket_success"), ephemeral=True, delete_after=10)


async def set_reaction_role(ctx: ContextMenuContext, _):
    bot = ctx.bot
    msg: Message = ctx.target
    role_select = RoleSelectMenu(
        custom_id="reaction_role_select",
        placeholder=_("set_reaction_role_select_placeholder"),
        min_values=1,
        max_values=1,
    )


async def send_embed(ctx, _):
    open_embedgenerator = Button(
        style=ButtonStyle.URL,
        label=_("misc_open_embed_generator"),
        url="https://embed.dan.onl/",
    )
    submit_url = Button(
        style=ButtonStyle.PRIMARY,
        label=_("misc_submit_embed_url"),
        custom_id="submit_embed_url",
    )
    embed = Embed(
        title=_("misc_send_embed_title"),
        description=_("misc_send_embed_description"),
        color=0x00FF00,
    )
    embed.set_image(
        "https://raw.githubusercontent.com/AITG-Discord-Bot/AITG-Web/refs/heads/main/imgs/embedjson.png"
    )
    await ctx.send(
        embeds=embed,
        components=[ActionRow(open_embedgenerator, submit_url)],
        ephemeral=True,
    )


async def move_all(ctx: SlashContext, _, target: GuildVoice | GuildStageVoice):
    author = ctx.author
    if not author.voice:
        await ctx.send(_("misc_not_in_voicechannel"), ephemeral=True)
        return
    authorvoicechannel = author.voice.channel
    if target == authorvoicechannel:
        await ctx.send(_("misc_same_voicechannel"), ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    is_error = False
    for member in authorvoicechannel.voice_members:
        try:
            await member.move(target.id)
        except:
            is_error = True
    if is_error:
        await ctx.send(_("misc_move_all_error"))
        return
    await ctx.send(_("misc_move_all_success"))
