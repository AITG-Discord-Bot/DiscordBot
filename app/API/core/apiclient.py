from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError
from aiohttp import ClientSession, ContentTypeError, ClientResponseError
from .model import APIRequestError, APIResponse
from common.core import var

T = TypeVar("T", bound=BaseModel)


class ApiClient:
    def __init__(self):
        self._session: Optional[ClientSession] = None

    async def get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession()
        return self._session

    async def request(
            self,
            endpoint: str,
            method: str = "GET",
            response_model: Optional[Type[T]] = None,
            **kwargs
    ) -> T | list[T] | Any:
        """
        공통 API 요청 메서드
        :param endpoint: 요청을 보낼 엔드포인트
        :param method: HTTP 메서드 (GET, POST, etc.)
        :param response_model: 응답 데이터를 파싱할 Pydantic 모델, list 형태로 반환 될 때에도 단일 객체 모델을 지정, 알아서 처리함
        :param kwargs: 추가 요청 매개변수 (headers, params, json, data 등)
        :return: 파싱된 응답 데이터, 형식이 지정이 안된 경우 원시 데이터 반환
        """
        url = var.apiurl + endpoint
        headers = kwargs.pop("headers", {})
        headers["X-Internal-Request"] = "true"

        params = kwargs.get("params")
        if params:
            kwargs["params"] = {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in params.items()}

        session = await self.get_session()

        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:

                try:
                    raw_body = await response.json()
                    api_res = APIResponse(**raw_body)

                except (ContentTypeError, ValueError, TypeError):
                    response.raise_for_status()
                    return await response.text()

                if not api_res.success:
                    raise APIRequestError(
                        error_code=api_res.error_code,
                        message=api_res.message or "Unknown error",
                        status=response.status,
                        data=api_res.data
                    )

                # 3. 데이터 반환 로직 (기존과 동일)
                if response_model and api_res.data is not None:
                    if isinstance(api_res.data, list):
                        return [response_model(**item) for item in api_res.data]
                    return response_model(**api_res.data)

                return api_res.data

        except APIRequestError as e:
            raise e

        except (ClientResponseError, ValidationError) as e:
            raise APIRequestError(data=str(e), message="ClientError", error_code=500)

    async def close(self):
        if self._session:
            await self._session.close()
