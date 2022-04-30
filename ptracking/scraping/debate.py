from collections import namedtuple
from functools import lru_cache
from typing import Union

import requests

DebateText = namedtuple("DebateText", ["title", "content"])

class DebateFetcher():
    def __init__(self, url: str) -> None:
        if "{debate_id}" not in url:
            raise KeyError("Trascript source URL must contain {debate_id}", url)
        self.url = url

    @lru_cache
    def fetch_debate_text(self, debate_id: str) -> Union[DebateText, None]:
        resp = requests.get(self.url.format(debate_id=debate_id))
        if resp.ok:
            title, _, content = resp.text.partition("\r\n")
            return DebateText(title=title.strip(), content=content.strip())
        # TODO Log that the request failed.
        return None
