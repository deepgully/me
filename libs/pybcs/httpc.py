#!/usr/bin/env python
#coding:utf8
import urllib
import urllib2
import httplib
import cookielib
import os
import re
import sys
import time
import copy
import hmac
import base64
import hashlib
import mimetypes

import socket
socket.setdefaulttimeout(60)

try:
    import json
except:
    import simplejson as json

try:
    from bae.api import logging as logger
except:
    import logging
    logger = logging.getLogger('pyhttpclient')

from cStringIO import StringIO
from urlparse import urlparse
from common import shorten

READ_BODY_TO_MEMORY = 1024*1024 # 1M

try:
    import pycurl
except:
    pass

#this is a function decorator, 
def network(func):
    '''
    这是一个decorator, 表示该函数会发出http 操作.
    '''
    if not hasattr(func, 'attr') : 
        func.attr = []
    func.attr += ['network']
    return func

###########################################################
# http client
# there is no unicode in this lib 
###########################################################

class HTTPException(Exception):
    '''
    描述一个HTTP 异常. 包含如下字段:
    e.status
    e.header
    e.body   
    '''
    def __init__(self, resp, msg=None):
        Exception.__init__(self)
        self.status = resp['status']
        self.header = resp['header']
        self.body   = resp['body']
        self.msg    = msg
        
        try:
            body = json.loads(self.body)
            self.errno = body['Error']['code']
            self.errmsg= body['Error']['Message']
        except Exception,e:
            self.errno = None
            self.errmsg= None
            
    def __str__(self):
        return "status:[%d]\nheader:%serrno:[%s]\nerrmsg:%s(%s)"%(self.status,self.header,self.errno,self.errmsg, str(self.msg))

class FilePartReader:
    '''
    用于上传文件的一部分
    '''
    def __init__(self, fp, start, length):
        self.fp = fp
        self.fp.seek(start)
        self.length = length

    def read_callback(self, size):
        if self.length == 0: # read all
            return ''
        if self.length > size:
            self.length -= size
            return self.fp.read(size)
        else :
            size = self.length
            self.length -= size
            return self.fp.read(size)
    def read_all(self):
        return self.read_callback(self.length)

class HTTPC:
    ''' define the http client interface'''
    def __init__(self):
        pass
        
    def get(self, url, headers={}):
        '''
        发起HTTP GET 请求
        '''
        raise NotImplementException()

    def head(self, url, headers={}):
        '''
        发起HTTP HEAD 请求
        '''
        raise NotImplementException()

    def put(self, url, body='', headers={}):
        '''
        发起HTTP PUT请求
        '''
        raise NotImplementException()

    def post(self, url, body='', headers={}):
        '''
        发起HTTP POST 请求
        '''
        raise NotImplementException()

    def delete(self, url, headers={}):
        '''
        发起HTTP DELETE 请求
        '''
        raise NotImplementException()

    def get_file(self, url, local_file, headers={}):
        '''
        发起HTTP GET 请求, 请求的响应body会写入到local_file
        '''
        raise NotImplementException()

    def put_file(self, url, local_file, headers={}):
        '''
        发起HTTP PUT 请求, 请求的body从local_file 中读取
        '''
        raise NotImplementException()

    def post_multipart(self, url, local_file, filename='file1', fields={}, headers={}):
        '''
        发起HTTP Multipart POST 请求
        if local_file is None, 
        we will just post fields
        '''
        raise NotImplementException()

    def put_file_part(self, url, local_file, start, length, headers={}):
        '''
        发起HTTP PUT 请求, 请求的body从local_file 中 start 处读出length 长度.
        '''
        raise NotImplementException()

    def _parse_resp_headers(self, resp_header):
        (status, header) = resp_header.split('\r\n\r\n') [-2] . split('\r\n', 1)
        status = int(status.split(' ')[1])

        header = [i.split(':', 1) for i in header.split('\r\n') ]
        header = [i for i in header if len(i)>1 ]
        header = [[a.strip().lower(), b.strip()]for (a,b) in header ]
        return (status, dict(header) )

class PyCurlHTTPC(HTTPC):
    '''
    HTTPC 的PyCurl 实现, 需要安装PyCurl
    '''
    def __init__(self, proxy = None, limit_rate = 0):
        # limit rate
        pass
		
    def get(self, url, headers={}):
        logger.info('pycurl -X GET "%s" ', url)
        self._init_curl('GET', url, headers)
        return self._do_request()

    def head(self, url, headers={}):
        logger.info('pycurl -X HEAD "%s" ', url)
        self._init_curl('HEAD', url, headers)
        return self._do_request()

    def delete(self, url, headers={}):
        logger.info('pycurl -X DELETE "%s" ', url)
        self._init_curl('DELETE', url, headers)
        return self._do_request()

    def get_file(self, url, local_file, headers={}):
        logger.info('pycurl -X GET "%s" > %s', url, local_file)
        self._init_curl('GET', url, headers, local_file)
        return self._do_request()

    def put(self, url, body='', headers={}):
        headers = copy.deepcopy(headers)
        logger.info('pycurl -X PUT -d "%s" "%s" ', shorten(body, 100), url)
        self._init_curl('PUT', url, headers)
        req_buf =  StringIO(body)
        self.c.setopt(pycurl.INFILESIZE, len(body)) 
        self.c.setopt(pycurl.READFUNCTION, req_buf.read)
        return self._do_request()

    def post(self, url, body='', headers={}, log=True):
        headers = copy.deepcopy(headers)
        if log: 
            logger.info('pycurl -X POST "%s" ', url)
        headersnew = { 'Content-Length': str(len(body))}
        headers.update(headersnew)
        self._init_curl('POST', url, headers)
        req_buf =  StringIO(body)
        self.c.setopt(pycurl.READFUNCTION, req_buf.read)
        return self._do_request()

    def put_file(self, url, local_file, headers={}):
        logger.info('pycurl -X PUT -T"%s" "%s" ', local_file, url)
        self._init_curl('PUT', url, headers)
        filesize = os.path.getsize(local_file) 
        self.c.setopt(pycurl.INFILESIZE, filesize) 
        self.c.setopt(pycurl.INFILE, open(local_file, 'rb')) 
        return self._do_request()

    #just for PyCurl
    def put_file_part(self, url, local_file, start, length, headers={}):
        logger.info('pycurl -X PUT -T"%s[%d->%d]" "%s" ', local_file, start, length, url)
        self._init_curl('PUT', url, headers)
        filesize = os.path.getsize(local_file) 

        self.c.setopt(pycurl.INFILESIZE, length) 
        self.c.setopt(pycurl.READFUNCTION, FilePartReader(open(local_file, 'rb'), start, length).read_callback)

        return self._do_request()

    def post_multipart(self, url, local_file, filename='file1', fields={}, headers={}):
        post_info = ' '.join( ['-F "%s=%s"' % (k,urllib.quote(v)) for (k,v) in fields.items()])
        if local_file: 
            post_info += ' -F "%s=@%s" ' % (filename, local_file)
        logger.info('pycurl -X POST %s "%s" ', post_info, url)
        self._init_curl('POST', url, headers)
        values = fields.items()
        if filename:
            values.append( (filename, (pycurl.FORM_FILE, local_file)) )
        self.c.setopt(pycurl.HTTPPOST, values)
        return self._do_request()

    def _do_request(self):
        try:
            self.c.perform()
        except pycurl.error, e:
            resp = {'status': 0, 
                    'header' : {}, 
                    'body': '', 
                    'body_file': '', 
                    }
            msg = str(e)
            raise HTTPException(resp, msg)

        resp_header = self.c.resp_header_buf.getvalue()
        resp_body = self.c.resp_body_buf.getvalue()
        status = self.c.getinfo(pycurl.HTTP_CODE)

        status, headers = self._parse_resp_headers(resp_header)
        self.c.close()
        
        rst = { 'status': status, 
                'header' : headers, 
                'body': resp_body, 
                'body_file': self.c.resp_body_file, 
                }
        if (status in [200, 206]): 
            return rst
        else:
            raise HTTPException(rst)

    def _init_curl(self, verb, url, headers, 
            resp_body_file=None):
        self.c = pycurl.Curl()
        self.c.resp_header_buf = None
        self.c.resp_body_buf = None
        self.c.resp_body_file = None

        self.c.setopt(pycurl.DEBUGFUNCTION, self._curl_log)
        self.c.setopt(pycurl.VERBOSE, 1)
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(pycurl.MAXREDIRS, 10)

        self.c.setopt(pycurl.SSL_VERIFYHOST, 0)
        self.c.setopt(pycurl.SSL_VERIFYPEER, 0)

        #self.c.setopt(pycurl.CONNECTTIMEOUT, 100)
        #self.c.setopt(pycurl.TIMEOUT, 60*60*3)

        self.c.unsetopt(pycurl.CUSTOMREQUEST)
        if verb == 'GET' : self.c.setopt(pycurl.HTTPGET, True)
        elif verb == 'PUT' : self.c.setopt(pycurl.UPLOAD , True)
        elif verb == 'POST' : self.c.setopt(pycurl.POST  , True)
        elif verb == 'HEAD' : self.c.setopt(pycurl.NOBODY, True)
        elif verb == 'DELETE' : self.c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        else: raise KeyError('unknown verb ' + verb)

        self.c.setopt(pycurl.URL, url)

        if headers:
            headers = ['%s: %s'%(k, v) for (k,v) in headers.items()]
            self.c.setopt(pycurl.HTTPHEADER, headers)

        self.c.resp_header_buf = StringIO()
        self.c.resp_body_buf = StringIO()
        self.c.setopt(pycurl.HEADERFUNCTION,    self.c.resp_header_buf.write)

        if resp_body_file: 
            self.c.resp_body_file = resp_body_file 
            f = open(resp_body_file, "wb")
            self.c.setopt(pycurl.WRITEDATA, f)
        else:
            self.c.setopt(pycurl.WRITEFUNCTION,     self.c.resp_body_buf.write)
    
    def _curl_log(self, debug_type, debug_msg):
        curl_out = [    pycurl.INFOTYPE_HEADER_OUT,         #2  find this out from pycurl.c
                        pycurl.INFOTYPE_DATA_OUT,           #4
                        pycurl.INFOTYPE_SSL_DATA_OUT]       #6
        curl_in  =  [   pycurl.INFOTYPE_HEADER_IN,          #1
                        pycurl.INFOTYPE_DATA_IN,            #3
                        pycurl.INFOTYPE_SSL_DATA_IN]        #5
        curl_info = [   pycurl.INFOTYPE_TEXT]               #0 

        if debug_type in curl_out:
            logger.debug("> %s" % debug_msg.strip())
        elif debug_type in curl_in:
            logger.debug("< %s" % debug_msg.strip())
        else:
            logger.debug("I %s" % (debug_msg.strip()) )


class HttplibHTTPC(HTTPC):
    '''
    HTTPC 的httplib 实现, 
    '''
    def __init__(self):
        pass
        
    #used by small response (get/put), not get_file
    def _request(self, verb, url, data, headers={}):
        response = self.send_request(verb, url, data, headers)
        if verb == 'HEAD':
            response.close()
            resp_body = ''
        else:
            resp_body = response.read()
        for (k, v) in response.getheaders():
            logger.debug('< %s: %s' % (k, v))

        logger.debug('< ' + shorten(data, 1024))
        response_headers = dict(response.getheaders())
        rst = { 'status': response.status, 
                'header' : response_headers, 
                'body': resp_body, 
                'body_file': None, 
                }

        if (response.status in [200, 206]): 
            return rst
        else:
            raise HTTPException(rst)

    def request(self, verb, url, data, headers={}):
        try:
            return self._request(verb, url, data, headers)
        except httplib.IncompleteRead, e:
            rst = { 'status': 0,
                   'header' : {}, 
                   'body': '', 
                   'body_file': '', 
                  }
            raise HTTPException(rst, 'transfer closed with bytes remaining to read !!! ' + str(e))

    #used by all 
    def send_request(self, verb, url, data, headers={}):
        logger.info('ll httplibcurl -X "%s" "%s" ', verb, url)
        for (k, v) in headers.items():
            logger.debug('> %s: %s' % (k, v))
        logger.debug('\n')
        logger.debug('> ' + shorten(data, 1024))
        o = urlparse(url)
        host = o.netloc
        path = o.path
        if o.query: 
            path+='?'
            path+=o.query

        if o.scheme == 'https':
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)
        conn.request(verb, path, data, headers)
        response = conn.getresponse()
        return response

    def get(self, url, headers={}):
        return self.request('GET', url, '', headers)

    def head(self, url, headers={}):
        return self.request('HEAD', url, '', headers)

    def put(self, url, body='', headers={}):
        headers = copy.deepcopy(headers)
        if 'content-length' not in headers:
            headers.update({'content-length': str(len(body)) })
        return self.request('PUT', url, body, headers)

    def post(self, url, body='', headers={}):
        headers = copy.deepcopy(headers)
        if 'Content-Type' not in headers:
            headers.update({'Content-Type': 'application/octet-stream'})
        if 'Content-Length' not in headers:
            headers.update({'Content-Length': str(len(body)) })
        return self.request('POST', url, body, headers)

    def delete(self, url, headers={}):
        return self.request('DELETE', url, '', headers)

    def get_file(self, url, local_file, headers={}):
        logger.info('httplibcurl -X GET "%s" > %s ', url, local_file)
        response = self.send_request('GET', url, '', headers)
        fout = open(local_file, 'wb')
        CHUNK = 1024*256
        while  True:
            data = response.read(CHUNK)
            if not data:
                break
            fout.write(data)
        fout.close()
        response_headers = dict(response.getheaders())

        rst = { 'status':  response.status, 
                'header' : response_headers, 
                'body':    None, 
                'body_file': local_file, 
                }

        #check if read all response
        bytes_readed = os.path.getsize(local_file)
        bytes_expected = int(response_headers['content-length'])
        bytes_remaining = bytes_expected - bytes_readed
        if bytes_remaining:
            raise HTTPException(rst, 'transfer closed with bytes remaining to read!!! %d bytes readed, %d bytes remained ' % (bytes_readed, bytes_remaining))

        if (response.status in [200, 206]): 
            return rst
        else:
            raise HTTPException(rst)

    def put_file(self, url, local_file, headers={}):
        logger.info('httplibcurl -X PUT -T "%s" %s ',  local_file, url)
        return self.put(url, open(local_file, 'rb').read(), headers)

    def post_multipart(self, url, local_file, filename='file1', fields={}, headers={}):
        logger.info('httplibcurl -X POST -F "%s" %s with fields: %s',  local_file, url, str(fields))
        headers = copy.deepcopy(headers)
        if local_file and filename:
            f = (filename, os.path.basename(local_file), open(local_file, 'rb').read())
            f_list = [f]
        else:
            f_list = []
        content_type, body = encode_multipart_formdata(fields.items(), f_list)
        headersnew = { 'Content-Type' : content_type,
                'Content-Length': str(len(body))}
        headers.update(headersnew)
        #req = urllib2.Request(url, body, headers)
        return self.post(url, body, headers) 

    def put_file_part(self, url, local_file, start, length, headers={}):
        logger.warn('it is a tragedy to use `put_file_part` by httplib , YoU NeeD pycurl installed! ')
        data = FilePartReader(open(local_file, 'rb'), start, length).read_all()
        return self.put(url, data, headers)

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % _get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY                                                                                             
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def select_best_httpc():
    import platform
    try:
        import pycurl
        logger.debug('use pycurl httpclient')
        return PyCurlHTTPC
    except :
        logger.debug('use httplib httpclient')
        return HttplibHTTPC

__all__ = ['network', 'HTTPException', 'PyCurlHTTPC', 'HttplibHTTPC', 'select_best_httpc']
