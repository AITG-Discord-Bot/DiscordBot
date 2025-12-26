from interactions import BaseContext, Permissions

from . import var, apirequest

admin_cache = {}


async def is_dev(ctx: BaseContext) -> bool:
    return int(ctx.author.id) in var.devs


async def is_admin(ctx: BaseContext) -> bool:
    global admin_cache
    author = ctx.author
    server = ctx.guild
    key_ = (int(server.id), int(author.id))  # TODO: 캐시 사용해서 성능 개선
    if author.has_permission(Permissions.ADMINISTRATOR):
        return True
    try:
        res = await apirequest(f"/server/{int(server.id)}/mods")
        res = int(res)
        for role in author.roles:
            if int(role.id) == res:
                return True
    except:
        return False
    return False
