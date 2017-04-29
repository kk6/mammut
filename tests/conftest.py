# -*- coding: utf-8 -*-
import os
import pytest

BASE_URL = 'https://friends.nico'


@pytest.fixture
def api_factory():
    class APIFactory:
        def create(self, base_url=BASE_URL):
            from mammut.api import Mammut
            from mammut.parsers import RawParser
            token = {'access_token': os.environ['MAMMUT_ACCESS_TOKEN']}
            return Mammut(token, base_url, parser=RawParser)
    return APIFactory()

