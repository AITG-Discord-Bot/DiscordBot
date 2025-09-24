from interactions import BaseContext, Permissions

from . import var, apirequest


async def is_dev(ctx: BaseContext) -> bool:
    return int(ctx.author.id) in var.devs


async def is_admin(ctx: BaseContext) -> bool:
    author = ctx.author
    server = ctx.guild
    if author.has_permission(Permissions.ADMINISTRATOR):
        return True
    try:
        res = await apirequest(f"/server/{int(server.id)}/mods")
        if int(author.id) in int(res["data"]):
            return True
    except:
        return False
    return False
