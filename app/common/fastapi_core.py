from typing import Callable, Coroutine, Any, Optional, Union
import inspect

from interactions import Client

AsyncFuncType = Callable[..., Coroutine[Any, Any, Any]]


class MyFunctions:
    logger = None

    def __init__(self, logger):
        self.logger = logger

    def set(self, name, value: AsyncFuncType) -> None:
        """
        Set the function by name
        :param name: name of the function
        :param value: Async function that will be called
        """
        if not inspect.iscoroutinefunction(value):
            raise ValueError(f"{name} is not a coroutine function")
        setattr(self, name, value)

    def remove(self, name: str) -> None:
        """
        Remove the function by name
        :param name: name of the function
        """
        if hasattr(self, name):
            delattr(self, name)

    def get(self, name) -> AsyncFuncType or None:
        """
        Get the function by name
        :param name: name of the function
        :return: function
        """
        return getattr(self, name)

    async def run(self, name: str, bot: Client, params: Optional[Union[dict, list]]):
        """
        Run the function by name
        :param name: name of the function
        :param bot: bot instance
        :param params: parameters to pass to the function
        :return: result of the function
        """
        func = self.get(name)
        if func is None:
            return None
        try:
            result = await func(bot, params)
            return result
        except Exception as e:
            self.logger.error(f"Error running function {name}: {e}")
            return None
