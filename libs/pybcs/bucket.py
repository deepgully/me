#!/usr/bin/env python
#coding:utf8

import time
import urllib

import common 
from httpc import *
from object import Object, Superfile

try:
    import json
except:
    import simplejson as json

class Bucket:
    ''' 
     bucket.create/ bucket.delete / bucket.setacl 
    '''
    def __init__(self, bcs, bucket_name):
        self.bcs = bcs
        self.host = bcs.host
        self.ak = bcs.ak 
        self.sk = bcs.sk 
        self.bucket_name = bucket_name
        self.sleep = 1 # sleep 1 second after upload

        self.put_url=bcs.sign('PUT', bucket_name, '/')
        self.get_url=bcs.sign('GET', bucket_name, '/')
        self.head_url=bcs.sign('HEAD', bucket_name, '/')
        self.del_url=bcs.sign('DELETE', bucket_name, '/')
        #self.c = self.bcs.c
        self.c = self.bcs.httpclient_class()

    def __str__(self):
        return '%s/%s' % (self.host, self.bucket_name)

    def object(self, object_name):
        """
        构造object对象
        参数：
            object_name:  object名称
        """
        return Object(self, object_name)

    def superfile(self, object_name, sub_object_list):
        """
        构造superfile对象
        参数：
            object_name:  需要创建的superfile object名称
            sub_object_list: 指定该superfile由哪些子文件构成.
        """
        return Superfile(self, object_name, sub_object_list)

    @network
    def create(self):
        """
        发起 create bucket 请求
        """
        return self.c.put(self.put_url, '')

    @network
    def delete(self):
        """
        发起 delete bucket 请求
        """
        return self.c.delete(self.del_url)

    @network
    def list_objects_raw(self, prefix='', start=0, limit=100):
        """
        列出该bucket 下的文件. 返回原始json 串.
            prefix: 返回以prefix 为前缀的object 列表
            start: 从第几个objcet 返回
            limit: 返回多少个object  (作用类似于sql的start, limit)
        """
        params = { 'start': start,
                  'limit': limit,
                 }
        if prefix:
            params.update ({'prefix': prefix})

        url = self.get_url + '&' + urllib.urlencode(params)

        rst = self.c.get(url)
        j = json.loads( rst['body'] )
        return j['object_list']

    @network
    def list_objects(self, prefix='', start=0, limit=100):
        """
        列出该bucket 下的文件. Object 列表
            prefix: 返回以prefix 为前缀的object 列表
            start: 从第几个objcet 返回
            limit: 返回多少个object  (作用类似于sql的start, limit)
        """
        '''return parsed object list'''
        lst = self.list_objects_raw(prefix, start, limit)
        return [self.object(o['object'].encode('utf-8')) 
                for o in lst] 
        
    #acl : string like: {statements':[{'user':['joe'],'resource':['bucket/object'],'action':['*'],'effect':'allow'}]}
    @network
    def set_acl(self, acl):
        """
        设置acl, 
            acl: acl 描述串
        """
        return self.c.put(self.put_url+'&acl=1', acl)

    @network
    def get_acl(self):
        """
        获取acl
        """
        return self.c.get(self.get_url+'&acl=1')

    @network
    def make_public(self):
        """
        设置bucket的访问权限为公开读（public-read）
        """
        acl = '{"statements":[{"action":["get_object"],"effect":"allow","resource":["%s\\/"],"user":["*"]}]}' % (self.bucket_name)
        self.set_acl(acl)

    @network
    def make_private_to_user(self, user):
        """
        设置bucket的访问权限为私有（private）
        """
        acl = '{"statements":[{"action":["*"],"effect":"allow","resource":["%s\\/"],"user":["%s"]}]}' % (self.bucket_name, user)
        self.set_acl(acl)

    @network
    def enable_logging(self, target_bucket, target_prefix='', headers=None): 
        pass

    def disable_logging(self, target_bucket, target_prefix='', headers=None): 
        pass



