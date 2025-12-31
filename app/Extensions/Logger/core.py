from interactions import *
from API.features.logger import loggerAPI, request as reqdto, response as resdto
from . import handler


async def setlogchannel(
    ctx: SlashContext, _, textchannel: BaseChannel, category: GuildCategory
):
    guildid = int(ctx.guild_id)
    categoryid = int(category.id)
    textchannelid = int(textchannel.id)
    if category.type != ChannelType.GUILD_CATEGORY:
        await ctx.send(_("logging_notacategory"), ephemeral=True)
        return
    if textchannel.type == ChannelType.GUILD_CATEGORY:
        await ctx.send(_("logging_notatextchannel"), ephemeral=True)
        return
    dto = reqdto.LogChannelReqDTO(serverid=guildid, logchannel=textchannelid, logcategory=categoryid)
    await loggerAPI.create_logchannel(dto)
    handler.func.add_logchannel(guildid, categoryid, textchannel)
    await ctx.send(_("logging_logchannel_set"), ephemeral=True)


async def dellogchannel(ctx: SlashContext, _, category: GuildCategory):
    categoryid = int(category.id)
    guildid = int(ctx.guild_id)
    await loggerAPI.delete_logchannel(guildid, categoryid)
    await ctx.send(_("logging_logchannel_deleted"), ephemeral=True)
