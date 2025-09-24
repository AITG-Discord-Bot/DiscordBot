import time
import threading
from collections import defaultdict
from typing import Union


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        """
        :param max_calls: 허용할 최대 호출 횟수
        :param period: 제한 시간 (초 단위)
        """
        self.max_calls = max_calls
        self.period = period
        self.lock = threading.Lock()
        self.calls = defaultdict(list)  # user별 호출 기록

    def get(self, user: Union[str, int]) -> bool:
        """
        :param user: 사용자 ID (문자열)
        :return: True(허용) / False(거부)
        """
        now = time.time()
        with self.lock:
            # 해당 유저의 오래된 기록 제거
            self.calls[user] = [t for t in self.calls[user] if t > now - self.period]

            if len(self.calls[user]) < self.max_calls:
                self.calls[user].append(now)
                return True
            else:
                return False
