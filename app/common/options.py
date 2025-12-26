from interactions import OptionType, slash_option, ChannelType
from .localization import getname, getdesc


def voicechannel(
    name="options_voicechannel", desc="options_voicechannel", required=True
):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.CHANNEL,
            required=required,
            channel_types=[ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE],
        )(func)

    return wrapper


def textchannel(name="options_textchannel", desc="options_textchannel", required=True):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.CHANNEL,
            required=required,
            channel_types=[
                ChannelType.GUILD_TEXT,
                ChannelType.GUILD_NEWS,
                ChannelType.GUILD_FORUM,
                ChannelType.GUILD_NEWS_THREAD,
                ChannelType.GUILD_PUBLIC_THREAD,
                ChannelType.GUILD_PRIVATE_THREAD,
                # 사실상 그냥 메시지 보낼 수 있는 채널들
            ],
        )(func)

    return wrapper


def category(name="options_category", desc="options_category", required=True):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.CHANNEL,
            required=required,
            channel_types=[ChannelType.GUILD_CATEGORY],
        )(func)

    return wrapper


def role(name="options_role", desc="options_role", required=True):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.ROLE,
            required=required,
        )(func)

    return wrapper


def integer(
    name="options_integer",
    desc="options_integer",
    required=True,
    min_value=None,
    max_value=None,
):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.INTEGER,
            required=required,
            min_value=min_value,
            max_value=max_value,
        )(func)

    return wrapper


def string(
    name="options_string",
    desc="options_string",
    required=True,
    min_length=None,
    max_length=None,
):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.STRING,
            required=required,
            min_length=min_length,
            max_length=max_length,
        )(func)

    return wrapper


def ephemeral(
    required=False,
):
    name = "options_ephemeral"
    desc = "options_ephemeral_desc"

    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.BOOLEAN,
            required=required,
        )(func)

    return wrapper


def member(name="options_member", desc="options_member", required=True):
    def wrapper(func):
        return slash_option(
            name=getname(name),
            description=getdesc(desc),
            opt_type=OptionType.USER,
            required=required,
        )(func)

    return wrapper
