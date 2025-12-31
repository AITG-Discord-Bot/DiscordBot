from typing import Optional, Any
from pydantic import BaseModel


class APIResponse(BaseModel):
    """공통 응답 규격 DTO"""
    success: bool
    message: Optional[str] = None
    error_code: Optional[int] = None
    data: Optional[Any] = None

class APIRequestError(Exception):
    def __init__(
            self,
            error_code: int,  # 여기도 int로 변경
            message: str = None,
            status: int = None,
            data: dict | str | None = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status = status
        self.data = data
        super().__init__(f"[{error_code}] {message}")