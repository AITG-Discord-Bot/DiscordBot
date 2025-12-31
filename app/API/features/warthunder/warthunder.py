from .clan import WarthunderClanAPI, response as clan_res, request as clan_req
from .news import WarthunderNewsAPI, response as news_res

class WarthunderAPI:
    def __init__(self):
        self.clan = WarthunderClanAPI()
        self.news = WarthunderNewsAPI()

class Request:
    def __init__(self):
        self.clan = clan_req

class Response:
    def __init__(self):
        self.news = news_res

warthunderAPI = WarthunderAPI()
request = Request()
response = Response()

__all__ = ["warthunderAPI", "request", "response"]