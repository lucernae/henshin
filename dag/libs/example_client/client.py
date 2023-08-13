import logging
from dataclasses import dataclass, asdict
from json import dumps

import requests


@dataclass
class SampleRequest:
    status: bool

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def dict(self):
        return self.__dict__

    @property
    def json(self):
        return dumps(self.__dict__)


@dataclass
class SampleResponse:
    id: int
    name: str
    status: bool

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def dict(self):
        return self.__dict__

    @property
    def json(self):
        return dumps(self.__dict__)


@dataclass
class SampleCollectionResponse:
    code: int
    errors: str
    result: list[dict | SampleResponse]

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def dict(self):
        return self.__dict__

    @property
    def json(self):
        return dumps(self.__dict__)

    def __post_init__(self):
        self.result = [SampleResponse(**v) if isinstance(v, dict) else v for v in self.result]


class Client:

    def __init__(self, username=None, password=None):
        """Simulate creating REST Client with username/pass creds"""
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self) -> requests.Response:
        """Faking a login"""
        r = self.session.get('https://httpbin.org')
        return r

    def do_something(self, request: SampleRequest = None) -> SampleCollectionResponse:
        """Simulate an API that receives request and returns response"""
        mock_json_data = [
            SampleResponse(1, 'Darth Maul', request.status),
            SampleResponse(2, 'Riou', request.status),
            SampleResponse(3, 'Lazlo', request.status),
            SampleResponse(4, 'Hugo', request.status),
        ]
        mock_collection_response = SampleCollectionResponse(
            code=200,
            errors="",
            result=mock_json_data,
        )
        logging.info(f'mock_response: {mock_collection_response.dict}')
        r = self.session.post(
            'https://httpbin.org/anything',
            json=mock_collection_response.dict
        )
        if r.status_code != 200:
            raise ValueError('fetch API failed')
        logging.info(f'json: {r.json()}')
        response_dict = r.json()['json']
        return SampleCollectionResponse(**response_dict)
