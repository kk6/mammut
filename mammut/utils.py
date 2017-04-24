# -*- coding: utf-8 -*-
import json
import mimetypes


def bundle_media_description(key, filename):
    """Bundle the media description necessary for uploading.

    :param key: form-data key name
    :param filename: Local file name or path.
    :return: tuple of ('key name', ('file name', 'file object', 'MIME content-type')
    :rtype: tuple

    """
    content_type, _ = mimetypes.guess_type(filename)
    media_description = (key, (filename, open(filename, 'rb'), content_type))
    return media_description


def store_json_to_file(filename, data, mode='w', indent=2, sort_keys=True):
    with open(filename, mode) as fp:
        json.dump(data, fp, indent=indent, sort_keys=sort_keys)
