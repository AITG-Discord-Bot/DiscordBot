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
from .options import ephemeral


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
    if ctx.guild:
        _ = localizator(ctx.guild.preferred_locale)
    error = event.error
    if isinstance(error, CommandCheckFailure):
        await ctx.send(_("error_check_failure"), ephemeral=True)
        return
    elif isinstance(error, CommandOnCooldown):
        err: CommandOnCooldown = error
        await ctx.send(
            _("error_oncooldown").format(round(err.cooldown.get_cooldown_time())),
            ephemeral=True,
        )
        return
    elif isinstance(error, MaxConcurrencyReached):
        await ctx.send(_("error_concurrency"), ephemeral=True)
        return
    elif isinstance(error, Forbidden):
        await ctx.send(_("error_forbidden"), ephemeral=True)
    elif isinstance(error, APIRequestError):
        logger.error("APIRequestError occurred", exc_info=error)
        await ctx.send(
            _(error.data if error.data else "error_apirequest"), ephemeral=True
        )
    else:
        logger.error("Unhandled command error", exc_info=error)
        try:
            await ctx.send(_("error_generic"), ephemeral=True)
        except Exception:
            pass


async def component_error_handler(event: ComponentError, logger):
    ctx = event.ctx
    locale = ctx.locale
    _ = localizator(locale)
    if ctx.guild:
        _ = localizator(ctx.guild.preferred_locale)
    error = event.error
    logger.warning(error)
    if isinstance(error, CommandCheckFailure):
        await ctx.send(_("error_check_failure"), ephemeral=True, components=[])
        return
    elif isinstance(error, Forbidden):
        await ctx.send(_("error_forbidden"), ephemeral=True, components=[])
        return
    elif isinstance(error, CommandOnCooldown):
        err: CommandOnCooldown = error
        await ctx.send(
            _("error_oncooldown").format(round(err.cooldown.get_cooldown_time())),
            ephemeral=True,
        )
        return
    elif isinstance(error, APIRequestError):
        logger.error("APIRequestError occurred", exc_info=error)
        await ctx.send(
            _(error.data if error.data else "error_apirequest"), ephemeral=True
        )
    else:
        logger.error("Unhandled Component error", exc_info=error)
        json = {
            "serverid": ctx.guild.id,
            "userid": ctx.author.id,
            "component": ctx.component.custom_id,
            "error": str(error),
        }
        await ctx.send(_("error_generic"), ephemeral=True, components=[])
        logger.error("에러가 발생했습니다.")
        logger.error(json)
