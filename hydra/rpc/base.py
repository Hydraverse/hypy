from __future__ import annotations
from requests import Response, Session

from hydra import log


class BaseRPC:
    __url = None
    __session = None

    class Error(BaseException):
        response: Response = None
        result: BaseRPC.Result = None

        def __init__(self, response: Response):
            self.response = response
            self.result = BaseRPC.Result(response.json()) if len(response.content) else None

        def __str__(self) -> str:
            return str(self.result) if self.result is not None else str(self.response)

        def __repr__(self) -> str:
            return repr(self.result) if self.result is not None else repr(self.response)

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
            raise BaseRPC.Error(rsp)

        json = rsp.json()

        if json["error"]:
            raise BaseRPC.Error(rsp)

        log.debug(f"result: {json}")

        return BaseRPC.Result(json)
