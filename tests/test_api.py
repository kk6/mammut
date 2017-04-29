# -*- coding: utf-8 -*-
import vcr

vtr = vcr.VCR(
    cassette_library_dir='cassettes',
    decode_compressed_response=True,
    serializer='json',
)


@vtr.use_cassette('cassettes/test_get_instance_info.json')
def test_get_instance_info(api_factory):
    api = api_factory.create()
    resp = api.get_instance_info()
    expected = {
        "description": "",
        "email": "",
        "title": "friends.nico",
        "uri": "friends.nico",
    }
    assert resp.json() == expected
