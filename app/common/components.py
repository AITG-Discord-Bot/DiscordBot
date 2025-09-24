from interactions import OptionType, slash_option, ChannelType
from .localization import getname, getdesc


def voicechannel(name="options.voicechannel", description="options.voicechannel.desc"):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(description),
            opt_type=OptionType.CHANNEL,
            required=False,
            channel_types=[ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE],
        )(func)

    return wrapper
