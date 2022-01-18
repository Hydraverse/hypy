from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

from requests import Response, Session
from attrdict import AttrDict

from hydra import log


class BaseRPC:
    __url = None
    __session = None

    class Exception(BaseException):
        response: Response = None
        error: BaseRPC.Result = None

        def __init__(self, response: Response):
            self.response = response
            self.error = BaseRPC.Result(response.json()) if len(response.content) else None

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

        def __init__(self, json: dict = None):
            if json is None:
                json = {}

            else:
                for key, value in json.items():
                    if isinstance(value, dict):
                        json[key] = BaseRPC.Result(value)
                    elif isinstance(value, list):
                        json[key] = BaseRPC.Result.__conv_list(value)

            super(BaseRPC.Result, self).__init__(json)

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

    def __init__(self, url: str):
        self.__url = url

    def __repr__(self):
        return f"{self.__class__.__name__}(url=\"{self.__url}\")"

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    def get(self, path: str) -> BaseRPC.Result:
        if self.__session is None:
            self.__session = Session()

        request_url = self.__build_request_path(path)

        log.debug(f"get [{request_url}]")

        rsp: Response = self.__session.get(
            url=request_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                "referer": request_url,
            }
        )

        if not rsp.ok:
            raise BaseRPC.Exception(rsp)

        json = rsp.json()

        if "error" in json and json["error"]:
            raise BaseRPC.Exception(rsp)

        log.debug(f"result: {json}")

        return BaseRPC.Result(json)

    def post(self, name: str, *args) -> BaseRPC.Result:
        if self.__session is None:
            self.__session = Session()

        request = BaseRPC.__build_request_dict(name, *args)

        log.debug(f"post [{self.__url}] {name} request={request}")

        rsp: Response = self.__session.post(
            url=self.__url,
            json=request
        )

        if not rsp.ok:
            raise BaseRPC.Exception(rsp)

        json = rsp.json()

        if json["error"]:
            raise BaseRPC.Exception(rsp)

        log.debug(f"result: {json}")

        return BaseRPC.Result(json)

    def __build_request_path(self, request_path: str) -> str:
        scheme, netloc, path, query, fragment = urlsplit(self.url)

        if request_path.startswith("/"):
            request_path = request_path[1:]

        path = os.path.join(path, request_path)

        return urlunsplit((scheme, netloc, path, query, fragment))

    @staticmethod
    def __build_request_dict(name: str, *args, id_: int = 1) -> dict:
        return {
            "id": id_,
            "jsonrpc": "2.0",
            "method": name,
            "params": list(args)
        }
