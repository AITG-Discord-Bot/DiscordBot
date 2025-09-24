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
    apirequest,
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


class MyLogger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.conn = None
        self.broadcastlevel = "info"

    def debug(self, msg, *args, **kwargs):
        return super(MyLogger, self).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return super(MyLogger, self).info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return super(MyLogger, self).error(msg, *args, **kwargs)


logging.setLoggerClass(MyLogger)
logger = logging.getLogger("AITG")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

debugfile = var.logpath + var.debugfile
file_debug_handler = logging.FileHandler(debugfile, encoding="utf-8", mode="w")
file_debug_handler.setLevel(logging.DEBUG)
file_debug_handler.setFormatter(formatter)
logger.addHandler(file_debug_handler)

errlogfile = var.logpath + var.errorfile
file_error_handler = logging.FileHandler(errlogfile, encoding="utf-8", mode="a")
file_error_handler.setLevel(logging.ERROR)
file_error_handler.setFormatter(formatter)
logger.addHandler(file_error_handler)

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
    # if var.server is None:
    #     await updatekoreandiscordbot()
    #     updatekoreandiscordbot.start()

    # check guild availability
    # await apirequest("/serverinfo/setavailability", params={"availability": 0})
    # for guild in bot.guilds:
    #     await apirequest("/serverinfo/add", params={"serverid": guild.id})
    # result = await apirequest("/serverinfo/deleteunavailable")
    # if result["data"] != 0:
    #     logger.info(f"Deleted {len(result['data'])} unavailable servers")
    #     for temp in result["data"]:
    #         logger.info(f"Deleted serverid: {temp}")


@slash_command(name="hello", description="Hello", scopes=[var.dev_server])
async def my_command_function(ctx: SlashContext):
    await ctx.send("안녕", ephemeral=True)


# @check(is_dev)
# @slash_command(
#     name="reload_ext", description="reload extension", scopes=[var.dev_server]
# )
# @extension()
# async def myreload(ctx: SlashContext, extension: str):
#     await myreload2(extension)
#     await ctx.send("Done", ephemeral=True)
#
#
# async def myreload2(extension):
#     if extension == "all":
#         for temp in Extensions:
#             if temp == "all":
#                 continue
#             bot.reload_extension(temp)
#     else:
#         bot.reload_extension(extension)


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
async def unloadext(ctx: SlashContext, extension: str):
    if extension == "all":
        for temp in Extensions:
            if temp == "all":
                continue
            bot.unload_extension(temp)
    else:
        bot.unload_extension(extension)
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

    # update_extensions()
    # print(Extensions)

    # if var.server is not None:
    #     bot.debug_scope = var.server
    #     logger.info(f"debug at server: {bot.debug_scope}")
    # bot.start(var.token)
