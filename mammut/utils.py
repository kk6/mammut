# -*- coding: utf-8 -*-
import os
import base64


def encode_image_file(filename):
    ext = os.path.splitext(filename)[1][1:]  # exclude dot.
    with open(filename, 'rb') as fp:
        encoded = base64.b64encode(fp.read())
        return b"data:image/" + ext.encode('utf8') + b';base64,' + encoded
