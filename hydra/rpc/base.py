from __future__ import annotations

from requests import Response, Session

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

    class Result(dict):

        def __init__(self, json: dict):

            def _convert(obj):

                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, dict):
                            obj[k] = BaseRPC.Result(v)
                        elif isinstance(v, list):
                            obj[k] = [_convert(item) for item in v]

                if isinstance(obj, list):
                    for idx, val in enumerate(obj):
                        if isinstance(val, dict):
                            obj[idx] = BaseRPC.Result(val)
                        elif isinstance(val, list):
                            obj[idx] = [_convert(item) for item in val]

                return obj

            if "result" in json or "error" in json:
                if "result" in json:
                    json["result"] = _convert(json["result"])

                if "error" in json:
                    json["error"] = _convert(json["error"])

                super().__init__(json)
            else:
                super().__init__(_convert(json))

        def __getattr__(self, item):
            return self.result.getdefault(item, self[item]) if "result" in self else self[item]

        def __setattr__(self, key, value):
            if "result" in self:
                self.result[key] = value
            else:
                self[key] = value

        def __str__(self):
            value = self.Value
            return str(value) if value is not self else super().__str__()

        @property
        def result(self):
            return self["result"]

        @property
        def error(self):
            return self["error"]

        # noinspection PyPep8Naming
        @property
        def Value(self):
            result = self.get("result", ...)
            error = self.get("error", ...)

            return error if error not in (None, ...) \
                else result if result is not ... \
                else error if error is not ... \
                else self

        def __serialize__(self, name="value"):
            o_v = self.Value
            return o_v if name is None else dict(
                (k, getattr(v, "__serialize__", lambda: v)()) for k, v in o_v.items()
            ) if isinstance(o_v, dict) else {name: o_v}

        @staticmethod
        def render(name: str, result, spaces=lambda lvl: "  " * lvl, longest=None, full=False):

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

    @property
    def url(self):
        return self.__url

    @staticmethod
    def __build_request_dict(name: str, *args, id_: int = 1) -> dict:
        return {
            "id": id_,
            "jsonrpc": "2.0",
            "method": name,
            "params": list(args)
        }

    def call(self, name: str, *args) -> BaseRPC.Result:
        if self.__session is None:
            self.__session = Session()

        request = BaseRPC.__build_request_dict(name, *args)

        log.debug(f"POST: {request}")

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
