from interactions import *
from common.localization import getname, getdesc


def use_personalrating():
    def wrapper(func):
        return slash_option(
            name=getname("options_use_personalrating"),
            description=getdesc("options_use_personalrating_desc"),
            opt_type=OptionType.BOOLEAN,
            required=False,
        )(func)

    return wrapper
