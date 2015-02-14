#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webtest import TestApp, Upload
from webtest.compat import to_bytes
import rest, unittest

class TestRestService(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(rest.app)
    
    def test_upload(self):
        self.file_name = '007lva.jpg'
        self.image = file('./source_test_images/%s' % self.file_name)
        self.uploaded_file_contents = self.image.read()
        self.resp = self.app.post('/Images',
                                  upload_files=[('file',
                                                 self.file_name,
                                                 self.uploaded_file_contents)])
        assert self.resp.status == '200 OK'
        
    def test_retrieve_image(self):
        self.file_name = '007lva.jpg'
        self.image = file('./source_test_images/%s' % self.file_name)
        self.uploaded_file_contents = self.image.read()
        self.app.post('/Images', upload_files=[('file', self.file_name,
                                                 self.uploaded_file_contents)])
        self.resp = self.app.get('/Images/1')
        assert self.resp.status == '200 OK'
        
    def test_retrieve_nonexistent_image(self):
        self.file_name = '007lva.jpg'
        self.image = file('./source_test_images/%s' % self.file_name)
        self.uploaded_file_contents = self.image.read()
        self.app.post('/Images', upload_files=[('file', self.file_name,
                                                 self.uploaded_file_contents)])
        self.resp = self.app.get('/Images/5', expect_errors = True, 
                                 status = 500)
        assert self.resp.status == '500 Internal Server Error'
        
    def test_prueba(self):
        self.resp = self.app.post('/test')
        assert self.resp.status == '200 OK'
    
    def test_error404(self):
        self.resp = self.app.get('/Dummy', expect_errors=True, status = 404)
        assert self.resp.status == '404 Not Found'
        
    def test_error400_with_badfile(self):
        self.file_name = 'bad_file_test.txt'
        self.image = file('./source_test_images/%s' % self.file_name)
        self.uploaded_file_contents = self.image.read()
        self.resp = self.app.post('/Images',
                                  upload_files=[('file',
                                                 self.file_name,
                                                 self.uploaded_file_contents)],
                                                 expect_errors=True, 
                                                 status = 400)
        assert self.resp.status == '400 Bad Request'

    def tearDown(self):
        pass