from __future__ import annotations

import json
import os
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

from requests import Response, Session
from attrdict import AttrDict

from hydra import log


class BaseRPC:
    __url = None
    __session = None
    __response_factory = None

    DEFAULT_GET_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    }

    DEFAULT_POST_HEADERS = {}

    class Exception(BaseException):
        response: Response = None
        error: BaseRPC.Result = None

        def __init__(self, response: Response):
            self.response = response
            try:
                self.error = BaseRPC.Result(response.json()) if len(response.content) else None
            except json.JSONDecodeError:
                self.error = BaseRPC.Result(str(response.content, encoding="utf-8"))

        def __str__(self) -> str:
            return str(self.error) if self.error is not None else str(self.response)

        def __repr__(self) -> str:
            return repr(self.error) if self.error is not None else repr(self.response)

        def __serialize__(self):
            return {
                "response": str(self.response),
                "error": self.error.__serialize__(name=None) if self.error else None
            }

    class Result(AttrDict):

        @staticmethod
        def __conv_list(lst):
            if isinstance(lst, list):
                return [
                    BaseRPC.Result(itm) if isinstance(itm, dict) else
                    BaseRPC.Result.__conv_list(itm) if isinstance(itm, list) else
                    itm
                    for itm in lst
                ]
            return lst

        def __init__(self, result: [dict, object] = None):
            if result is None:
                json_ = {}
            elif not isinstance(result, dict):
                json_ = {"result": result}
            else:
                json_ = result

                for key, value in json_.items():
                    if isinstance(value, dict):
                        json_[key] = BaseRPC.Result(value)
                    elif isinstance(value, list):
                        json_[key] = BaseRPC.Result.__conv_list(value)

            super(BaseRPC.Result, self).__init__(json_)

        def __str__(self):
            value = self.Value
            return str(value) if value is not self else super().__str__()

        # noinspection PyPep8Naming
        @property
        def Value(self):
            result = self.get("result", ...)
            error = self.get("error", ...)

            return error if error not in (None, ...) \
                else result if result is not ... \
                else error if error is not ... \
                else self

        def __serialize__(self, name: Optional[str] = "value"):
            o_v = self.Value

            stringify = lambda v: (
                v if isinstance(v, (list, tuple, dict, set, str, int, float))
                else str(v)
            )

            return (
                stringify(o_v) if name is None

                else {
                    k: getattr(v, "__serialize__", lambda: stringify(v))() for k, v in o_v.items()

                } if isinstance(o_v, dict)

                else [
                    getattr(v, "__serialize__", lambda: stringify(v))() for v in o_v
                    # Deeper nested lists will not be serialized

                ] if isinstance(o_v, list)

                else {name: stringify(o_v)}
            )

        def render(self, name: str, spaces=lambda lvl: "  " * lvl, longest: int = None, full: bool = False):
            result = self.Value

            if not isinstance(result, (list, dict)):
                yield str(result)
                return

            flat = BaseRPC.Result.flatten(name, result, full=full)

            if not longest:
                flat = list(flat)
                longest = max(len(row[0]) + len(spaces(row[2])) for row in flat) + 4

            for label, value, level in flat:
                yield f"{spaces(level)}{label}".ljust(longest) \
                      + (str(value) if value is not ... else "")

        @staticmethod
        def flatten(name: str, result, level: int = 0, full: bool = False) -> dict:
            if not isinstance(result, (list, dict)):
                yield name, result, level
                return

            yield name, ..., level

            if isinstance(result, list):
                for index, value in enumerate(result):
                    yield from BaseRPC.Result.flatten(
                        (name if full else "")  # name.rsplit(".", 1)[0] if "." in name else name)
                        + f"[{index}]", value, level=level + 1, full=full
                    )
            else:
                for key, value in result.items():
                    yield from BaseRPC.Result.flatten(
                        (name if full else "") + f".{key}", value, level=level + 1, full=full
                    )

    def __init__(self, url: str, *, response_factory=None):
        self.__url = url
        self.__response_factory = (
            response_factory
            if response_factory is not None else
            BaseRPC.RESPONSE_FACTORY_RSLT
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

    RESPONSE_FACTORY_RSLT = lambda rsp: BaseRPC.Result(rsp.json())
    RESPONSE_FACTORY_JSON = lambda rsp: rsp.json()

    def request(self, *, request_type: str, path: Optional[str], response_factory=None, **kwds):
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

    def get(self, path: str, *, headers: Optional[dict] = None, response_factory=None) -> [BaseRPC.Result, Response, object]:
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

    def post(self, path: str, *, request_type: str = "post", headers: Optional[dict] = None, response_factory=None, **request) -> [BaseRPC.Result, Response]:
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

