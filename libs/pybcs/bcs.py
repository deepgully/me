#!/usr/bin/env python
#coding:utf8

import urllib
import re, sys, os

import time
import hmac, base64, hashlib

try:
    import json
except:
    import simplejson as json

import common
from bucket import Bucket
from httpc import *

class BCS:
    def __init__(self, host, ak , sk, httpclient_class=None):
        try:
            from bae.core import const
            self.host = (host if host else const.BCS_ADDR)
            self.ak   = (ak if ak else const.ACCESS_KEY)
            self.sk   = (sk if sk else const.SECRET_KEY)

            self.httpclient_class = HttplibHTTPC
        except:
            self.host = host
            self.ak = ak
            self.sk = sk
            self.httpclient_class = httpclient_class
            if not httpclient_class:
                self.httpclient_class = select_best_httpc()
        if self.host.endswith('/') :
            self.host = host[:-1]
        if not self.host.startswith('http'):
            self.host = "http://" + self.host
        
        self.c = self.httpclient_class()
        self.get_url=self.sign('GET', '', '/')

    @network
    def list_buckets(self):
        """
        列举所有的buckets
        """
        rst = self.c.get(self.get_url)
        text = rst['body']
        j = json.loads(text)
        return [self.bucket(b['bucket_name'].encode('utf8')) for b in j]

    def bucket(self, bucket_name):
        """
        构造bucket对象
        参数：
            bucket_name:  bucket名称
        """
        b = Bucket(self, bucket_name)
        return b

    #M(必选): request method. eg: PUT,GET,POST,DELETE,HEAD
    #B(必选): bucketname
    #O(必选): objectname
    #T(可选): 访问时间范围
    #I(可选):  访问ip限制
    #S(可选): 操作object大小限制
    #NOTICE: 请保证输入统一，比如B,O都应该同为unicode或同为utf8
    def sign(self, M, B, O, T=None, I=None, S=None):
        """
        计算签名，仅供内部使用
        参数：
            M: HTTP方法
            B: bucket name
            O: object name
            T: time
            I: IP
            S: size
        """
        flag = ''
        s =  ''
        flag+='M'; s += 'Method=%s\n' % M; 
        flag+='B'; s += 'Bucket=%s\n' % B; 
        flag+='O'; s += 'Object=%s\n' % O; 
        if T :   flag+='T'; s += 'Time=%s\n'   % T; 
        if I :   flag+='I'; s += 'Ip=%s\n'     % I; 
        if S :   flag+='S'; s += 'Size=%s\n'   % S; 

        s = '\n'.join([flag, s])
        
        def h(sk, body):
            digest = hmac.new(sk, body, hashlib.sha1).digest()
            t = base64.encodestring(digest)
            return urllib.quote(t.strip())

        sign = h(self.sk, s)
        url = '%s/%s%s?sign=%s:%s:%s' % (
                self.host, B, '/' + urllib.quote(O[1:]), 
                flag, self.ak, sign)
        if T :      url += '&time=%s'   % T;
        if I :      url += '&ip=%s'     % I; 
        if S :      url += '&size=%s'   % S; 
        return url
