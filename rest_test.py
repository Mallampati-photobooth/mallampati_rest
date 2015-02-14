#!/usr/bin/env python

from webtest import TestApp, compat
import rest, unittest

class TestRestService(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(rest.app)

    def test_upload(self):
        self.file_name = '007lva.jpg'
        with open('./source_test_images/%s' % self.file_name, 'rb')\
            as self.image:
            self.content = compat.to_bytes(self.image.read())
            self.resp = self.app.post('/Images', upload_files=[('file',
                                                                self.file_name,
                                                                self.content)])
            self.assertEqual(self.resp.status, '200 OK')
    
    def test_retrieve_image(self):
        self.file_name = '007lva.jpg'
        with open('./source_test_images/%s' % self.file_name, 'rb')\
            as self.image:
            self.content = compat.to_bytes(self.image.read())
            self.app.post('/Images', upload_files=[('file',
                                                    self.file_name,
                                                    self.content)])
        self.resp = self.app.get('/Images/1')
        self.assertEqual(self.resp.status, '200 OK')

    def test_retrieve_nonexistent_image(self):
        self.file_name = '007lva.jpg'
        with open('./source_test_images/%s' % self.file_name, 'rb')\
            as self.image:
            self.content = compat.to_bytes(self.image.read())
            self.app.post('/Images', upload_files=[('file',
                                                    self.file_name,
                                                    self.content)])
        self.resp = self.app.get('/Images/4', expect_errors = True, 
                                 status = 500)
        self.assertEqual(self.resp.status, '500 Internal Server Error')

    def test_error404(self):
        self.resp = self.app.get('/Dummy', expect_errors=True, status = 404)
        self.assertEqual(self.resp.status, '404 Not Found')

    def test_error400_with_badfile(self):
        self.file_name = 'bad_file_test.txt'
        with open('./source_test_images/%s' % self.file_name, 'rb')\
            as self.image:
            self.content = compat.to_bytes(self.image.read())
            self.resp = self.app.post('/Images', 
                                      upload_files=[('file',
                                                     self.file_name,
                                                     self.content)],
                                                     expect_errors = True,
                                                     status = 400)
        self.assertEqual(self.resp.status, '400 Bad Request')

    def tearDown(self):
        pass
    
