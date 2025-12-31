from interactions import *
from common.discordbot import safe_send
from Extensions.Server.model import ServerBase


async def send_as_notification(ctx: ContextMenuContext):
    target_message: Message = ctx.target
    content_text = target_message.content
    bot: Client = ctx.bot

    for attachment in target_message.attachments:
        content_text += f"\n{attachment.url}"

    target_embeds = target_message.embeds

    for server in bot.guilds:
        server_obj = ServerBase(ctx.bot, server.id)
        await server_obj.get()

        sent_msg = None

        if server_obj.botmessagechannel:
            sent_msg = await safe_send(
                ctx.bot,
                server_obj.botmessagechannel,
                content=content_text,
                embeds=target_embeds,
            )

        if not sent_msg:
            for channel in server.channels:
                channeltype = channel.type
                if channeltype != ChannelType.GUILD_TEXT:
                    continue

                sent_msg = await safe_send(
                    ctx.bot,
                    channel,
                    content=content_text,
                    embeds=target_embeds,
                )

                if sent_msg:
                    break
