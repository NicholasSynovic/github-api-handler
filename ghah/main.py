import re
from abc import ABCMeta, abstractmethod
from pprint import pprint
from re import Match
from typing import List, Protocol, Tuple

from requests import Response
from requests import get as reqGet


class GH_REST_Protocol(Protocol):
    endpoint: str
    reqHeaders: dict[str, str]


class GH_REST_ABC(GH_REST_Protocol, metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> Tuple[Response, dict]:
        ...

    @abstractmethod
    def _parseRespHeaders(self, resp: Response) -> dict:
        ...


class GH_REST(GH_REST_ABC):
    def __init__(self, endpoint: str, reqHeaders: dict) -> None:
        self.endpoint = endpoint
        self.reqHeaders = reqHeaders

    def get(self) -> Tuple[Response, dict]:
        resp: Response = reqGet(url=self.endpoint, headers=self.reqHeaders)
        respHeaders: dict = self._parseRespHeaders(resp=resp)

        return (resp, respHeaders)

    def _parseRespHeaders(self, resp: Response) -> dict:
        respHeaders: dict = dict(resp.headers)
        link: str = respHeaders["Link"]

        splitLink: List[str] = [l.strip() for l in link.split(sep=",")]
        lastLink: str = [l for l in splitLink if l.find('rel="last"') > -1][0]

        match: Match[str] | None = re.search(pattern=r"page=(\d+)", string=lastLink)

        lastPageNumber: int = 1
        if match:
            lastPageNumber: int = int(match.group(1))

        respHeaders["Last-Page"] = lastPageNumber
        return respHeaders
