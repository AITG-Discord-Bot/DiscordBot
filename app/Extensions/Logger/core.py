from interactions import *
from common import apirequest
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
    json = {"serverid": guildid, "logchannel": textchannelid, "logcategory": categoryid}
    await apirequest("/logger/channels", json=json, method="POST")
    handler.func.add_logchannel(guildid, categoryid, textchannel)
    await ctx.send(_("logging_logchannel_set"), ephemeral=True)


async def dellogchannel(ctx: SlashContext, _, category: GuildCategory):
    categordid = int(category.id)
    guildid = int(ctx.guild_id)
    await apirequest(f"/logger/channels/{guildid}/{categordid}", method="DELETE")
    await ctx.send(_("logging_logchannel_deleted"), ephemeral=True)
