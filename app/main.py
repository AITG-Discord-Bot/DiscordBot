import asyncio
import importlib
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Union, List

from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from interactions import *
from interactions.api.events import Startup, Error, CommandError, ComponentError
from common.guards import is_dev
from error_handler import (
    command_error_handler,
    on_error_handler,
    component_error_handler,
)
from common.core import MyFunctions, var, set_logger
from common.localization import load_localization

"""
mainframe of bot
using extensions: each command is separated into different files
                  easy to extend
                  no need to turn off bot to add new commands
"""

logger = set_logger(broadcast_delay=120, broadcast_initial=False)
# ------------------------------------------------------------
# Bot & Utilities
# ------------------------------------------------------------
bot = Client(
    intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.GUILD_MEMBERS,
    sync_interactions=True,
    fetch_members=True,
    logger=logger,
    # send_default_errors=False,
    activity="DM for support!",
    delete_unused_application_cmds=True,
)

# 전역 함수 컨테이너(Startup 이전에 준비되어야 extension 로딩 시 인자로 전달 가능)
functions = MyFunctions(logger)


# ------------------------------------------------------------
# Slash option decorator for "extension" arg
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Extensions 목록 관리
# ------------------------------------------------------------
Extensions: List[str] = []


def update_extensions():
    """Extensions/**/entry.py 경로를 모듈경로로 수집 (예: Extensions.x.y.entry)."""
    base = Path("Extensions")
    modules: list[str] = []
    if base.exists():
        for p in base.rglob("entry.py"):  # 재귀적으로 탐색: Extensions/**/entry.py
            try:
                rel = p.with_suffix("").relative_to(base)  # Extensions 기준 상대경로
            except ValueError:
                continue  # base 밖이면 스킵
            # 상대 경로의 각 파트를 '.'로 이어붙여 모듈 경로 생성
            mod = "Extensions." + ".".join(
                rel.parts
            )  # e.g., x/y/entry -> Extensions.x.y.entry
            modules.append(mod)
    uniq = sorted(set(modules))
    global Extensions
    Extensions = uniq + (["all"] if "all" not in uniq else [])


# ------------------------------------------------------------
# Listeners
# ------------------------------------------------------------
@listen(Startup)
async def on_startup():
    """
    on startup, load up all extensions safely
    """
    update_extensions()
    for temp in Extensions:
        if temp == "all":
            continue
        bot.load_extension(temp, functions=functions)
    logger.info("Bot is ready")
    logger.warning("bot started")


@listen(Error)
async def on_error(error: Error):
    await on_error_handler(error, logger)


@listen(CommandError, disable_default_listeners=True)
async def my_error_handler(event: CommandError):
    await command_error_handler(event, logger)


@listen(ComponentError, disable_default_listeners=True)
async def my_component_error_handler(event: ComponentError):
    await component_error_handler(event, logger)


# ------------------------------------------------------------
# Commands
# ------------------------------------------------------------
@slash_command(name="hello", description="Hello", scopes=var.dev_servers)
async def my_command_function(ctx: SlashContext):
    await ctx.send("안녕", ephemeral=True)


@check(is_dev)
@slash_command(name="load_ext", description="load extension", scopes=var.dev_servers)
@extension()
async def loadext(ctx: SlashContext, extension: str):
    load_localization()
    if extension == "all":
        for ext in Extensions:
            if ext != "all":
                try:
                    bot.load_extension(ext, functions=functions)
                except Exception as e:
                    await ctx.send(f"Failed to load {ext}: {e}", ephemeral=True)
                    return
        await ctx.send("All extensions loaded", ephemeral=True)
    else:
        try:
            bot.load_extension(extension, functions=functions)
            await ctx.send(f"Extension {extension} loaded", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Failed to load {extension}: {e}", ephemeral=True)


@check(is_dev)
@slash_command(
    name="unload_ext", description="unload extension", scopes=var.dev_servers
)
@extension()
async def unloadext(ctx: SlashContext, extension: str, send_response: bool = True):
    if extension == "all":
        for ext in Extensions:
            if ext != "all":
                try:
                    bot.unload_extension(ext)
                    importlib.invalidate_caches()
                    sys.modules.pop(ext, None)
                except Exception as e:
                    if send_response:
                        await ctx.send(f"Failed to unload {ext}: {e}", ephemeral=True)
                    return
        if send_response:
            await ctx.send("All extensions unloaded", ephemeral=True)
    else:
        try:
            bot.unload_extension(extension)
            if send_response:
                await ctx.send(f"Extension {extension} unloaded", ephemeral=True)
        except Exception as e:
            if send_response:
                await ctx.send(f"Failed to unload {extension}: {e}", ephemeral=True)
    update_extensions()


@check(is_dev)
@slash_command(
    name="reload_ext", description="reload extension", scopes=var.dev_servers
)
@extension()
async def reloadext(ctx: SlashContext, extension: str):
    await unloadext(ctx, extension, send_response=False)
    await loadext(ctx, extension)


@check(is_dev)
@slash_command(
    name="reload_extensionlist",
    description="reloads list of extensions",
    scopes=var.dev_servers,
)
async def reload_extensionlist(ctx: SlashContext):
    update_extensions()
    await ctx.send("Done", ephemeral=True)


# 자동완성: 입력 텍스트가 포함된 후보만 최대 25개 반환
@global_autocomplete("extension")
async def autocomplete(ctx: AutocompleteContext):
    query = (ctx.input_text or "").lower()
    candidates = [e for e in Extensions if query in e.lower()]
    await ctx.send(choices=candidates[:25])


# ------------------------------------------------------------
# FastAPI / Lifespan
# ------------------------------------------------------------
debugMode = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global debugMode
    if debugMode:
        bot.debug_scope = var.dev_servers
        logger.info("Bot starting in debug mode")
    asyncio.create_task(bot.astart(var.token))
    yield


app = FastAPI(lifespan=lifespan, root_path=var.app_root)


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
    hdr = request.headers.get("X-Internal-Request")
    if not hdr or hdr.lower() != "true":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    params = params or {}
    if not hasattr(functions, functionname):
        return JSONResponse({"error": "Function not found"}, status_code=404)

    logger.info(f"API call: {functionname} with params: {params}")
    result = await functions.run(functionname, bot, params)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=var.app_port)