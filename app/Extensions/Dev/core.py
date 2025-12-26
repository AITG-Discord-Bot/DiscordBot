from interactions import *
from common import apirequest, safe_send
from Extensions.Server.model import ServerBase


async def send_as_notification(ctx: ContextMenuContext):
    message = ctx.message
    context = message.content
    for attachment in message.attachments:
        context += f"\n{attachment.url}"

    for server in ctx.bot.servers:
        server = ServerBase(ctx.bot, server.id)
        await server.get()
        if server.botmessagechannel:
            await safe_send(
                ctx.bot,
                server.botmessagechannel,
                content=context,
                embeds=message.embeds,
            )
