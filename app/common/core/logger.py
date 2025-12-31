import logging
import os
import asyncio
import threading
import sys
import aiohttp
from common.core import var


class LogFlare(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.conn = None
        self.project_name: str | None = None
        self.project_key: str | None = None
        self.broadcasturl: str | None = None
        self.broadcastlevel: int = logging.WARNING
        self.broadcast: bool = False

    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Project": self.project_name,
            "ProjectKey": "Bearer " + self.project_key,
        }

    def test_connection(self) -> bool:
        """동기 함수에서 비동기 연결 테스트 실행"""
        try:
            self._spawn_coro(self._test_connection())
            return True
        except Exception:
            return False

    async def _test_connection(self) -> bool:
        self.info("\n\n====================\nTesting LogFlare Connection\n====================\n\n")
        if not (self.project_name and self.project_key and self.broadcasturl):
            self.warning("\n\n====================\nLogFlare Info InComplete\n====================\n\n")
            return False
        payload = {"errortype": "Test", "level": "INFO", "message": "Test connection", "test":True}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.broadcasturl, json=payload, headers=self.headers()
                ) as resp:
                    self.info(f"\n\n====================\nLogFlare connection test status: {resp.status}\n====================\n\n")
                    return resp.status < 400
        except Exception:
            self.exception("\n\n====================\nLogFlare connection test failed\n====================\n\n")
            return False

    def _spawn_coro(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:

            def _runner():
                try:
                    asyncio.run(coro)
                except Exception as e:
                    print(f"[Broadcast THREAD EXC] {e!r}")

            threading.Thread(target=_runner, daemon=True).start()
        else:
            loop.create_task(coro)

    def set_broadcastlevel(self, level: int) -> None:
        self.broadcastlevel = level

    async def _enable_broadcast_after(self, delay: float) -> None:
        await asyncio.sleep(delay)
        self.broadcast = True
        super().info(f"logger.broadcast enabled after {delay:.1f}s")

    def enable_broadcast_after(self, delay: float) -> None:
        """루프 유무와 상관없이 delay 후 broadcast=True로 전환"""
        if delay <= 0:
            self.broadcast = True
            return
        self._spawn_coro(self._enable_broadcast_after(delay))

    async def broadcast_(self, errortype, level_name: str, msg: str) -> None:
        if not (self.project_name and self.project_key and self.broadcasturl):
            return
        payload = {"errortype": errortype, "level": level_name, "message": msg}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.broadcasturl, json=payload, headers=self.headers()
                ) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        print(f"[Broadcast FAIL] {resp.status} {text}")
        except Exception as e:
            print(f"[Broadcast EXC] {e!r}")

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        try:
            formatted = (msg % args) if args else str(msg)
        except Exception:
            formatted = str(msg)

        errortype = None
        if exc_info:
            if isinstance(exc_info, tuple):
                errortype = getattr(exc_info[0], "__name__", None)
            elif isinstance(exc_info, BaseException):
                errortype = type(exc_info).__name__
            else:
                exc_type, _, _ = sys.exc_info()
                if exc_type:
                    errortype = exc_type.__name__

        if errortype is None and isinstance(msg, BaseException):
            errortype = type(msg).__name__

        if self.broadcast and level >= self.broadcastlevel:
            level_name = logging.getLevelName(level)
            self._spawn_coro(self.broadcast_(errortype, level_name, formatted))

        super()._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def warning(self, msg, *args, **kwargs):
        return self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self._log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        return self._log(logging.ERROR, msg, args, exc_info=exc_info, **kwargs)


def set_logger(
    name="AITG", *, broadcast_delay: float = 0.0, broadcast_initial: bool = False
) -> LogFlare:
    """
    Set up and return a logger instance

    :param name: The name of the logger
    :param broadcast_delay: The delay before enabling broadcast in seconds
    :type broadcast_delay: float
    :param broadcast_initial: Whether to enable broadcast initially
    :type broadcast_initial: bool
    :return: Logger instance
    :rtype: LogFlare
    """
    logging.setLoggerClass(LogFlare)
    logger: LogFlare = logging.getLogger(name)  # type: ignore
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_debug_handler = logging.FileHandler(var.debugfile, encoding="utf-8", mode="w")
    file_debug_handler.setLevel(logging.DEBUG)
    file_debug_handler.setFormatter(formatter)
    logger.addHandler(file_debug_handler)

    file_error_handler = logging.FileHandler(var.errorfile, encoding="utf-8", mode="a")
    file_error_handler.setLevel(logging.ERROR)
    file_error_handler.setFormatter(formatter)
    logger.addHandler(file_error_handler)

    logger.set_broadcastlevel(logging.WARNING)
    logger.broadcasturl = os.getenv("LOGFLARE_URL", "")
    logger.project_name = os.getenv("DISCORD_LOGFLARE_NAME", "")
    logger.project_key = os.getenv("DISCORD_LOGFLARE_KEY", "")
    logger.test_connection()

    logger.broadcast = broadcast_initial
    if broadcast_delay > 0:
        logger.enable_broadcast_after(broadcast_delay)

    return logger


def get_logger(name="AITG") -> LogFlare:
    return logging.getLogger(name)  # type: ignore
