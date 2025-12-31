from datetime import datetime
from typing import Dict, Optional

from interactions import GuildForum, Message
from API.features.logger import request
from dataclasses import dataclass

@dataclass
class CacheItem:
    msg: Message
    time: datetime
    dto: request.MessageLogReqDTO


logchannels = {}
messagecache: Dict[int, CacheItem] = {}
support_forum: Optional[GuildForum] = None
forumthreads = {}
devmention = None
