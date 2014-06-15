# -*- coding: utf-8 -*-

import httplib
import urllib
import time
try:
    import hashlib as md5
except:
    import md5
try:
    import simplejson as json
except:
    import json
from urlparse import urlparse
import copy
from .log import getLogger
from .exceptions import BaeParamError, BaeValueError, BaeOperationFailed  

LOG = getLogger("bae.utils.log")

def connectoBackend(params, need = [], token = False, debug = False, **kwargs):
    class RequestCore(object):
        def __init__(self, url):
            _url = urlparse(url)
            host = _url.netloc
            self.path = _url.path
            if _url.scheme == 'https':
                self.handle = httplib.HTTPSConnection(host)
            else:
                self.handle = httplib.HTTPConnection(host)

        def __del__(self):
            self.handle.close()
        
        def send_request(self, method, body = '', headers ={}):
            self.handle.request(method, self.path, body, headers)
            _response = self.handle.getresponse()
            return (_response.status, _response.getheaders(), _response.read())

    class ResponseCore(object):
        def __init__(self, code, header, body):
            self.code = code
            self.header = header
            self.body = body

        def isOK(self):
            if self.code in (200, 201, 204, 206):
                return True
            return False

    class KeyDict:
        def __init__(self, dict):
            self._d = dict

        def __str__(self):
            return self._d.__str__()

        def __getattr__(self, name):
            if name in self._d:
                return self._d.get(name)
            raise KeyError(name)

        def __deepcopy__(self, memo):
            return KeyDict(copy.deepcopy(self._d))

        def update(self, dict):
            self._d.update(dict)

    #Users need to provide ['PRODUCT', 'NAME', 'DEFAULT_NAME']
    commonKeys = KeyDict(dict(
        TIMESTAMP    = 'timestamp',  
        METHOD       = 'method',
        EXPIRES      = 'expires',
        VERSION      = 'v',
        HOST         = 'host',
        ACCESS_TOKEN = 'access_token',
        ACCESS_KEY   = 'client_id',
        SECRET_KEY   = 'client_secret',
        SIGN         = 'sign',

        PRODUCT      = None,
        NAME         = None,
        DEFAULT_NAME = None,
    ))

    keys = copy.deepcopy(commonKeys)
    keys.update(kwargs)  
       
    def adjustQuery(params, need):
        params[keys.TIMESTAMP] = int(time.time())
        
        content = {}
        data = []
        need += [keys.TIMESTAMP, keys.METHOD]
        if keys.EXPIRES in params:
            need.append(keys.EXPIRES)
        if keys.VERSION in params:
            need.append(keys.VERSION)
        exclude = [keys.HOST]
        if not token:
            need.append(keys.ACCESS_KEY)
            exclude.append(keys.SECRET_KEY)
        else: 
            need.append(keys.ACCESS_TOKEN)

        for key in set(need):
            if key not in params or (not isinstance(params[key], int) and not params[key]):
                raise BaeParamError("Lack of parameter: ", key)
            if key in exclude:
                continue
            if not token: data.append((key, params[key]))
            content[key] = params[key]
        for key, value in params.items():
            if key not in need and key not in exclude:
                if not token: data.append((key, value))
                content[key] = value
                
        if not token:
            data.sort(key = lambda x:x[0])
            url = ''.join(['http://', params[keys.HOST], '/rest/2.0/', keys.PRODUCT, '/'])
            if keys.NAME in params:
                if not isinstance(params[keys.NAME], basestring):
                    raise BaeParamError("Resource name must be basestring", params[keys.NAME], type(params[keys.NAME]))
                if params[keys.NAME].find(' ') != -1:
                    raise BaeParamError("Response name can't contain spaces", params[keys.NAME])
                url += params[keys.NAME]
                data.remove((keys.NAME, params[keys.NAME]))
            else: url += keys.DEFAULT_NAME 
             
            basicString = 'POST' + url
            s = ''.join('%s=%s' %(k, v) for k, v in data)
            basicString += s + params[keys.SECRET_KEY]
            sign = md5.md5(urllib.quote_plus(basicString)).hexdigest()
            content[keys.SIGN] = sign

        content[keys.HOST] = params[keys.HOST]
        return content        
 
    def baseControl(params):
        def mkQuery(q):
            for k, v in q.items():
                if isinstance(v, unicode):
                    q[k] = v.encode('utf-8')
            return urllib.urlencode(q)

        resource = keys.DEFAULT_NAME
        if keys.NAME in params:
            resource = params.pop(keys.NAME)
        host = params.pop(keys.HOST)
        if not token:
            url = ''.join(['http://', host, '/rest/2.0/', keys.PRODUCT, '/', resource])
        else:    
            url = ''.join(['https://', host, '/rest/2.0/', keys.PRODUCT, '/', resource])
        query = RequestCore(url)
        body = mkQuery(params)
        if debug:
            LOG.info("url: (%s), body: (%s)" % (url, body[0:1024]))
        res = query.send_request(
            'POST', 
            body = body, 
            headers = {
                'Content-Type':'application/x-www-form-urlencoded', 
                'User-Agent':'Baidu Python Client'
                }
            )
        return ResponseCore(res[0], res[1], res[2])
 
    cont = adjustQuery(params, need)
    ret = baseControl(cont)
    return ret

def handleResponse(response, callback = None, debug = False):
    try:
        ret = json.loads(response.body)
    except Exception:
        raise BaeValueError("Invalid response body", response.body)

    if debug:
        LOG.info(str(ret)[0:1024])

    request_id = -1
    if 'request_id' in ret:
        request_id = ret['request_id']

    if response.isOK():
        if callable(callback):
            return request_id, callback(response.body)
        return request_id, ret

    raise BaeOperationFailed("Request failed",
        request_id, ret['error_code'], ret['error_msg'])
