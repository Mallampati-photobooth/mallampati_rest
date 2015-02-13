#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webtest import TestApp, Upload
from webtest.compat import to_bytes
import rest

def test_upload():
    app = TestApp(rest.app)
    file_name = '007lva.jpg'
    image = file('./source_test_images/%s' % file_name)
    uploaded_file_contents = image.read()
    resp = app.post('/Images', upload_files=[('file', file_name, uploaded_file_contents)])
    assert resp.status == '200 OK'
