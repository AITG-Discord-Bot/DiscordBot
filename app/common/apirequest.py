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
    params = kwargs.get("params")
    if params:
        kwargs["params"] = {
            k: (str(v).lower() if isinstance(v, bool) else v) for k, v in params.items()
        }

    async with ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            if get_text:
                return await response.text()
            return await response.json()


# TODO: 이거 message에 endpoint.errocde 이런식으로 들어가길 원함
async def apirequest(
    endpoint: str, method: str = "GET", surpress_error: bool = False, **kwargs
) -> list | dict | str | int | bool | None:
    """
    Make an API request to the specified endpoint with error handling.
    surpress_error 가 True 면 .get("success", False)로 성공여부 확인 가능
    :param surpress_error: If True, do not raise exceptions on API errors.
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
        if surpress_error:
            return {"success": False, "code": str(e.status), "message": e.message}
        raise APIRequestError(
            code=str(e.status), message=f"HTTP {e.status} {e.message}", status=e.status
        ) from e
    if not body.get("success", False):
        if surpress_error:
            return body
        raise APIRequestError(
            code=body.get("error_code"),
            message=body.get("message", "Unknown error"),
            status=body.get("error_code"),
            data=body.get("data"),
        )
    if surpress_error:
        return {"success": True, "data": body.get("data")}
    return body.get("data")
