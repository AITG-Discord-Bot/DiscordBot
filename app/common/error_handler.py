import traceback

from interactions.api.events import Error, CommandError, ComponentError
from interactions.client.errors import (
    Forbidden,
    CommandCheckFailure,
    CommandOnCooldown,
    MaxConcurrencyReached,
)

from common import APIRequestError, apirequest
from .localization import localizator, default_locale


async def on_error_handler(error: Error, logger):
    ctx = error.ctx
    if isinstance(error, Forbidden):
        await ctx.send("해당 명령어를 위한 권한이 부족합니다!", ephemeral=True)
    else:
        logger.error(traceback.format_exc(), exc_info=True)
        if ctx is not None:
            await ctx.send(f"에러가 발생했습니다.\n{type(error)}", ephemeral=True)


async def command_error_handler(event: CommandError, logger):
    ctx = event.ctx
    _ = localizator(default_locale)
    error = event.error
    if isinstance(error, CommandCheckFailure):
        await ctx.send("명령어를 실행하기에 권한이 부족합니다.", ephemeral=True)
        return
    elif isinstance(error, CommandOnCooldown):
        err: CommandOnCooldown = error
        await ctx.send(
            _("command_on_cooldown_err").format(
                round(err.cooldown.get_cooldown_time())
            ),
            ephemeral=True,
        )
        return
    elif isinstance(error, MaxConcurrencyReached):
        await ctx.send(
            "명령어를 사용할 수 있는 최대 동시성이 초과되었습니다.", ephemeral=True
        )
        return
    elif isinstance(error, Forbidden):
        await ctx.send("해당 명령어를 위한 권한이 부족합니다!", ephemeral=True)
    elif isinstance(error, APIRequestError):
        logger.error("APIRequestError")
        logger.error(error.message)
        logger.error(error.data)
    else:
        logger.error(error)
        logger.error(traceback.print_exception(error))
        # json = {
        #     "serverid": ctx.guild.id,
        #     "userid": ctx.author.id,
        #     "command": ctx.command.name.get_locale("korean"),
        #     "error": str(error),
        # }
        # erridx = await apirequest("/error/add", json=json)
        # await ctx.send(
        #     f"에러가 발생했습니다.\n에러번호: `{erridx['data']}`", ephemeral=True
        # )


async def component_error_handler(event: ComponentError, logger):
    ctx = event.ctx
    locale = ctx.locale
    _ = localizator(locale)
    error = event.error
    logger.warning(error)
    if isinstance(error, CommandCheckFailure):
        await ctx.send(_("check_failed_err"), ephemeral=True, components=[])
        return
    elif isinstance(error, Forbidden):
        await ctx.send(_("missing_permission_err"), ephemeral=True, components=[])
        return
    elif isinstance(error, CommandOnCooldown):
        err: CommandOnCooldown = error
        await ctx.send(
            _("command_on_cooldown_err").format(
                round(err.cooldown.get_cooldown_time())
            ),
            ephemeral=True,
        )
        return
    else:
        logger.error(error)
        logger.error(traceback.print_exception(error))
        json = {
            "serverid": ctx.guild.id,
            "userid": ctx.author.id,
            "component": ctx.component.custom_id,
            "error": str(error),
        }
        # erridx = await apirequest("/error/add", json=json)
        # await ctx.send(f"에러가 발생했습니다.\n에러번호: `{erridx['data']}`",
        # ephemeral=True)
        await ctx.send(_("error_occurred_err"), ephemeral=True, components=[])
        logger.error("에러가 발생했습니다.")
        logger.error(json)
