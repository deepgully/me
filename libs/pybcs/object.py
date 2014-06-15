#!/usr/bin/env python
#coding:utf8

import os

import common
from common import FileSystemException
import urllib
from httpc import *

class NameException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'NameExecption: ' + str(self.msg)

    
class Object:
    def __init__(self, bucket, object_name):
        if object_name[0] != '/':
            raise NameException('object name must start with "/"')
        
        self.bcs = bucket.bcs
        self.bucket = bucket
        
        self.object_name = object_name
        #self.c = self.bcs.c
        self.c = self.bcs.httpclient_class()
        self.etag = None

        bcs = bucket.bcs
        bucket_name = bucket.bucket_name

        self.put_url=bcs.sign('PUT', bucket_name, object_name)
        self.post_url=bcs.sign('POST', bucket_name, object_name)
        self.get_url=bcs.sign('GET', bucket_name, object_name)
        self.head_url=bcs.sign('HEAD', bucket_name, object_name)
        self.del_url=bcs.sign('DELETE', bucket_name, object_name)

        self.public_get_url = '%s/%s%s' % ( self.bcs.host, bucket_name, 
                                                  '/' + urllib.quote(object_name[1:]) )


    def __str__(self):
        return '%s/%s%s' % (self.bcs.host, self.bucket.bucket_name, self.object_name)

    def ref_str(self):
        return '%s/%s%s' % ('bs:/', self.bucket.bucket_name, self.object_name)

    def assert_file_writeable(self, path):
        if os.path.isdir(path): 
            raise FileSystemException(path + ' is not a file')

    def handle_response(self, r):
        try:
            self.etag = r['header']['etag']
            self.version = r['header']['x-bs-version']
        except:
            pass
        return r

    @network
    def put(self, content, headers={}):
        r = self.c.put(self.put_url, content, headers)
        return self.handle_response(r)

    
    @network
    def put_file(self, local_file, headers={}):
        """
        以PUT的方式上传文件
        参数：
            local_file:  本地文件名
        """
        self.assert_file_writeable(local_file)
        r = self.c.put_file(self.put_url, local_file, headers)
        return self.handle_response(r)

    def put_file_part(self, local_file, start, length, headers={}):
        """
        以PUT的方式上传文件片段
        参数： 
            local_file: 要上传的文件
            start:      文件内容起始位置
            length:     文件内容长度
        """
        self.assert_file_writeable(local_file)
        r = self.c.put_file_part(self.put_url, local_file, start, length, headers)
        return self.handle_response(r)

    
    def post(self, content, headers={}):
        ''' we can't create a object by post content
        Use put content instead
        '''
        raise NotImplementException()

    @network
    def post_file(self, local_file, headers={}):
        """
        以POST的方式上传文件
        参数：
            local_file:  本地文件名
        """
        self.assert_file_writeable(local_file)
        r = self.c.post_multipart(self.post_url, local_file, 'file1', headers)
        return self.handle_response(r)


    @network
    def get_to_file(self, local_file, headers={}):
        """
        下载object对应的文件
        参数：
            local_file:  文件下载后保存的名称
        """ 
        self.assert_file_writeable(local_file)
        r = self.c.get_file(self.get_url, local_file, headers)
        return self.handle_response(r)

    @network
    def get(self, headers={}):
        """
        获取object对应文件的内容
        返回值：正常情况下返回文件内容；出错情况下抛出异常
        """
        r = self.c.get(self.get_url, headers)
        return self.handle_response(r)

    @network
    def head(self, headers={}):
        """
        获取object的META信息
        """
        r = self.c.head(self.head_url, headers)
        return self.handle_response(r)


    @network
    def delete(self, headers={}):
        """
        删除object，用户必须有删除权限，才能执行成功
        """
        return self.c.delete(self.del_url, headers)

    #it's do a copy to self
    @network
    def setmeta(self, headers={}):
        return self.copy_to(self, headers)

    @network
    def copy_to(self, dst, headers={}):
        """
        复制当前object到dst object
        参数：
            dst: 目的object名称
        """
        headers.update( {
                'x-bs-copy-source': self.ref_str() ,
                'x-bs-copy-source-directive': 'copy', # copy or replace
                })
        return self.c.put(dst.put_url, '', headers)

    @network
    def copy_from(self, dst, headers={}):
        """
        将dst object复制到当前object
        参数：
            src: 源object名称
        """
        headers.update( {
                'x-bs-copy-source': dst.ref_str() ,
                'x-bs-copy-source-directive': 'copy', # copy or replace
                })
        return self.c.put(self.put_url, '', headers)



    @network
    def set_acl(self, acl, headers={}):
        """
        设置访问权限
        """
        r = self.c.put(self.put_url+'&acl=1', acl, headers)

    @network
    def get_acl(self, headers={}):
        """
        获取访问权限
        """
        r = self.c.get(self.get_url+'&acl=1', headers)
        return r

    @network
    def make_public(self):
        """
        设置object的访问权限为公开读（public-read）
        """
        acl = '{"statements":[{"action":["get_object"],"effect":"allow","resource":["%s%s"],"user":["*"]}]}' % (self.bucket.bucket_name, self.object_name)
        self.set_acl(acl)

    @network
    def make_private_to_user(self, user):
        """
        设置object的访问权限为私有（private）
        """
        acl = '{"statements":[{"action":["*"],"effect":"allow","resource":["%s%s"],"user":["%s"]}]}' % (self.bucket.bucket_name,self.object_name, user)
        self.set_acl(acl)


class Superfile(Object):
    def __init__(self, bucket, object_name, object_list):
        Object.__init__(self, bucket, object_name)
        self.object_list = object_list 

    
    def assertSubObjectExist(self):
        for o in self.object_list:
            if not o.etag:
                o.head() # get etag

    @network
    def put(self, headers={}):
        """
        根据子文件生成superfile
        """
        self.assertSubObjectExist()
        tmp_list = ['"part_%d": {"url": "%s", "etag":"%s"}' % (idx, o.ref_str(), o.etag)  
                for idx, o in enumerate(self.object_list)]
        tmp_list = ','.join(tmp_list)  
        self.superfile_meta = '{"object_list": {%s}}' % tmp_list
        url = '%s&superfile=1' % self.put_url

        return self.c.put(url, self.superfile_meta, headers)


    @network
    def put_file(self, local_file, headers={}):
        raise NotImplementException()

    @network
    def put_file_retain_versions(self, local_file, headers={}):
        raise NotImplementException()

    @network
    def post_file(self, local_file, headers={}):
        raise NotImplementException()

    @network
    def post_file_retain_versions(self, local_file, headers={}):
        raise NotImplementException()


