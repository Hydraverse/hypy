from __future__ import annotations

import json
import os
from typing import Optional, Callable, Any
from urllib.parse import urlsplit, urlunsplit

from requests import Response, Session
from attrdict import AttrDict

from hydra import log

from ..util.asyncc import AsyncMethods


class BaseRPC:
    __url: str
    __session: Session = None
    __response_factory: Callable[[Response], Any]

    asyncc: AsyncMethods

    DEFAULT_GET_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    }

    DEFAULT_POST_HEADERS = {}

    RESPONSE_FACTORY_RESP = lambda response: response

    @staticmethod
    def RESPONSE_FACTORY_JSON(rsp: Response) -> [AttrDict, str]:
        try:
            return rsp.json(object_hook=AttrDict)
        except json.JSONDecodeError:
            return str(rsp.content, encoding="utf-8")

    class Exception(BaseException):
        response: Response
        error: Optional[AttrDict, str]

        def __init__(self, response: Response):
            self.response = response

            try:
                if len(response.content):
                    rslt = BaseRPC.RESPONSE_FACTORY_JSON(response)

                    if "error" in rslt:
                        rslt = rslt.error
                else:
                    rslt = None

                self.error = rslt
            except json.JSONDecodeError:
                self.error = str(response.content, encoding="utf-8")

        def __str__(self) -> str:
            return str(self.error) if self.error is not None else str(self.response)

        def __repr__(self) -> str:
            return repr(self.error) if self.error is not None else repr(self.response)

    def __init__(self, url: str, *, response_factory: Callable[[Response], Any] = None):
        self.asyncc = AsyncMethods(self)

        self.__url = url

        self.__response_factory = (
            response_factory
            if response_factory is not None else
            BaseRPC.RESPONSE_FACTORY_JSON
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(url=\"{self.__url}\")"

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    @property
    def session(self):
        if self.__session is None:
            self.__session = Session()

        return self.__session

    @property
    def response_factory(self):
        return self.__response_factory

    def request(self, *, request_type: str, path: Optional[str], response_factory: Callable[[Response], Any] = None, **kwds) -> [Response, Any]:
        session = self.session
        request_fn = getattr(session, request_type, None)

        if not callable(request_fn):
            raise ValueError(f"Unknown request_type '{request_type}'")

        request_url = self.__build_request_url(path)

        log.debug(f"{request_type} [{request_url}]")

        rsp: Response = request_fn(
            url=request_url,
            **kwds
        )

        if not rsp.ok:
            raise BaseRPC.Exception(rsp)

        return (
            response_factory(rsp)
            if response_factory is not None else
            self.__response_factory(rsp)
        )

    def get(self, path: str, *, headers: Optional[dict] = None, response_factory: Callable[[Response], Any] = None) -> [Response, Any]:
        request_headers = dict(self.DEFAULT_GET_HEADERS)

        request_headers.update({
            "referer": self.url
        })

        if headers is not None and len(headers):
            request_headers.update(headers)

        return self.request(
            request_type="get",
            path=path,
            response_factory=response_factory,
            headers=request_headers,
        )

    def post(self, path: str, *, request_type: str = "post", headers: Optional[dict] = None, response_factory: Callable[[Response], Any] = None, **request) -> [Response, Any]:
        request_headers = dict(self.DEFAULT_POST_HEADERS)

        if headers is not None:
            request_headers.update(headers)

        return self.request(
            request_type=request_type,
            path=path,
            response_factory=response_factory,
            headers=request_headers,
            json=request,
        )

    def __build_request_url(self, request_path: Optional[str]) -> str:
        if request_path is None or not len(request_path):
            return self.url

        scheme, netloc, path, query, fragment = urlsplit(self.url)

        path = os.path.join(path, request_path)  # if request_path[0] == '/', this overwrites anything in the existing path.

        return urlunsplit((scheme, netloc, path, query, fragment))

