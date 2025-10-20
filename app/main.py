import asyncio
import json
import logging
import pkgutil
from contextlib import asynccontextmanager
from typing import Optional, Union

import interactions
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from interactions import (
    slash_command,
    SlashContext,
    slash_option,
    listen,
    Intents,
    check,
    global_autocomplete,
    OptionType,
    AutocompleteContext,
)
from interactions.api.events import Startup, Error, CommandError, ComponentError

from common import (
    logger,
    is_dev,
    command_error_handler,
    on_error_handler,
    component_error_handler,
    MyFunctions,
)
from common import var

"""
mainframe of bot
using extensions: each command is seperated into different files
                  easy to extend
                  no need to turn off bot to add new commands
"""


bot = interactions.Client(
    intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.GUILD_MEMBERS,
    sync_interactions=True,
    fetch_members=True,
    logger=logger,
    # send_default_errors=False,
    activity="AITG!",
)


def extension():
    """Call with `@extension()`"""

    def wrapper(func):
        return slash_option(
            name="extension",
            description="extension name",
            opt_type=OptionType.STRING,
            required=True,
            autocomplete=True,
        )(func)

    return wrapper


Extensions = []


def update_extensions():
    global Extensions
    Extensions = []
    for loader, module_name, is_pkg in pkgutil.iter_modules(
        ["Extensions"], "Extensions."
    ):
        Extensions.append(module_name)
    Extensions.append("all")


@listen(Startup)
async def on_startup():
    """
    on startup, load up all extesions
    """
    update_extensions()
    for temp in Extensions:
        if temp == "all":
            continue
        bot.load_extension(temp, functions=functions)
    logger.info("Bot is ready")
    logger.error("Bot is ready")


@slash_command(name="hello", description="Hello", scopes=[var.dev_server])
async def my_command_function(ctx: SlashContext):
    await ctx.send("안녕", ephemeral=True)


@check(is_dev)
@slash_command(
    name="reload_ext", description="reload extension", scopes=[var.dev_server]
)
@extension()
async def myreload(ctx: SlashContext, extension: str):
    await unloadext(ctx, extension=extension, send=False)
    await loadext(ctx, extension=extension)


@check(is_dev)
@slash_command(name="load_ext", description="load extension", scopes=[var.dev_server])
@extension()
async def loadext(ctx: SlashContext, extension: str):
    if extension == "all":
        for temp in Extensions:
            if temp == "all":
                continue
            bot.load_extension(temp, functions=functions)
    else:
        bot.load_extension(extension, functions=functions)
    await ctx.send("Done", ephemeral=True)


@check(is_dev)
@slash_command(
    name="unload_ext", description="unload extension", scopes=[var.dev_server]
)
@extension()
async def unloadext(ctx: SlashContext, extension: str, send=True):
    if extension == "all":
        for temp in Extensions:
            if temp == "all":
                continue
            bot.unload_extension(temp)
    else:
        bot.unload_extension(extension)
    if send:
        await ctx.send("Done", ephemeral=True)


@check(is_dev)
@slash_command(
    name="reload_extensionlist",
    description="reloads list of extensions",
    scopes=[var.dev_server],
)
async def reload_extensionlist(ctx: SlashContext):
    update_extensions()
    await ctx.send("Done", ephemeral=True)


@global_autocomplete("extension")
async def autocomplete(ctx: AutocompleteContext):
    await ctx.send(choices=Extensions)


@listen(Error)
async def on_error(error: Error):
    await on_error_handler(error, logger)


@listen(CommandError, disable_default_listeners=True)
async def my_error_handler(event: CommandError):
    await command_error_handler(event, logger)


@listen(ComponentError, disable_default_listeners=True)
async def my_component_error_handler(event: ComponentError):
    await component_error_handler(event, logger)


debugMode = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global debugMode
    if debugMode:
        bot.debug_scope = var.dev_server
        logger.info("Bot starting.in debug mode")
    asyncio.create_task(bot.astart(var.token))
    yield


app = FastAPI(lifespan=lifespan, root_path=var.app_root)
functions = MyFunctions(logger)


@app.post("/call/{functionname}")
async def discordbot(
    request: Request,
    functionname: str,
    params: Optional[Union[dict, list]] = Body(None),
):
    """
    FastAPI endpoint to call discordbot functions
    :param functionname: name of the function to call
    :param params: parameters to pass to the function
    :return: result of the function
    """
    if request.headers.get("X-Internal-Request").lower() != "true":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    # params: json string
    params = params or {}
    # Check if the function exists in the bot
    if not hasattr(functions, functionname):
        return JSONResponse({"error": "Function not found"})
    # Run the function
    logger.info(f"API call: {functionname} with params: {params}")
    result = await functions.run(functionname, bot, params)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=var.app_port)
