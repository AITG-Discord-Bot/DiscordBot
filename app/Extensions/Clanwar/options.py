from interactions import slash_option, OptionType

from common.localization import getname, getdesc


def partyid():
    def wrapper(func):
        return slash_option(
            name=getname("clanwar_option_partyid"),
            description=getdesc("clanwar_option_partyid_desc"),
            opt_type=OptionType.STRING,
            required=True,
            autocomplete=True,
        )(func)

    return wrapper
