from interactions import Client, Message, ComponentContext, Member, User
from interactions.api.events import Component


async def waitforcomponent(
    bot: Client, author: Member | User, message: Message, components, timeout=60
) -> ComponentContext | None:
    async def check(component: Component) -> bool:
        if component.ctx.author == author:
            return True
        else:
            await component.ctx.send("Not You!", ephemeral=True, delete_after=5)
            return None

    try:
        used_ctx = await bot.wait_for_component(
            components=components, check=check, timeout=timeout
        )
    except TimeoutError:
        await message.delete()
        return
    return used_ctx.ctx
