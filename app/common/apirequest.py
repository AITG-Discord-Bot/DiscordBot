from aiohttp import ClientSession, ClientResponseError
from . import var
from urllib.parse import urljoin


class APIRequestError(Exception):
    def __init__(
        self,
        code: str,
        message: str = None,
        status: int = None,
        data: dict | str | None = None,
    ):
        self.code = code
        self.message = message
        self.status = status
        self.data = data
        super().__init__(f"{code}: {message}")


async def make_request(method: str, url: str, get_text: bool = False, **kwargs):
    async with ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            if get_text:
                return await response.text()
            return await response.json()


# TODO: 이거 message에 endpoint.errocde 이런식으로 들어가길 원함
async def apirequest(
    endpoint: str, method: str = "GET", **kwargs
) -> list | dict | str | int | bool | None:
    """
    Make an API request to the specified endpoint with error handling.
    :param endpoint:
    :param method:
    :param kwargs:
    :return: Response data
    """
    url = var.apiurl + endpoint
    header = {"X-Internal-Request": "true"}
    if "headers" in kwargs:
        kwargs["headers"].update(header)
    else:
        kwargs["headers"] = header
    try:
        body = await make_request(method, url, **kwargs)
    except ClientResponseError as e:
        raise APIRequestError(
            code=str(e.status), message=f"HTTP {e.status} {e.message}", status=e.status
        ) from e

    if not body.get("success", False):
        raise APIRequestError(
            code=body.get("error_code"),
            message=body.get("message", "Unknown error"),
            status=body.get("error_code"),
            data=body.get("data"),
        )
    return body.get("data")
