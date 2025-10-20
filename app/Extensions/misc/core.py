from interactions import *
from common import waitforcomponent


async def send_to_channel_(ctx: ContextMenuContext, _):
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
