# -*- coding: utf-8 -*-

import sys
import socket
try:
    import cPickle as pickle
except ImportError:
    import pickle

from bae_utils.check import checkParamsType
from bae_utils.log import getLogger
from bae_memcache import mcpack
from bae_memcache import nshead

LOG = getLogger("bae.cache.log")

class BaeMemcacheException(Exception):
    pass
class BaeMemcacheInternalError(BaeMemcacheException):
    pass
class BaeMemcacheParamsError(BaeMemcacheException):
    pass

class BaeMemcache(object):
    CACHE_MAX_KEY_LEN = 180
    CACHE_MAX_VALUE_LEN = 1048576
    CACHE_MAX_QUERY_NUM = 64
 
    def __init__(self, cache_id, memcache_addr, user, password):
        checkParamsType([(memcache_addr, [basestring]), (user, [basestring]), (password, [basestring]), (cache_id, [basestring])])
       
        self._ak = user
        self._sk = password
        self._appid = cache_id
 
        self.nsh = nshead.CNsHead()
        self.lastcmd, self.lastkey = None, None
        self.lasterrno, self.lasterrmsg = 0, None
    
        self._servers = [] 
        for server in memcache_addr.split(";"):
            try:
                host, port = server.split(':')
                self._servers.append((host, int(port)))
            except:
                raise BaeMemcacheParamsError("Invalid memcache_addr")
        self._index = 0
        self._sock = None

    def __del__(self):
        self.__close_connection()

    def __get_connection(self):
        if self._sock: 
            return self._sock
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._index += 1
            if self._index >= len(self._servers):
                self._index = 0
            address = self._servers[self._index]
            s.connect(address)
            self._sock = s
            return self._sock
        except Exception, e:
            return None

    def __close_connection(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def __buildQuery(self, cmd, content):
        query = {}
        query['cmd'] = cmd
        query['pname'] = self._ak
        query['token'] = self._sk
        query['appid'] = self._appid 
        query['logid'] = 0
        query['content'] = {}
        query_num = len(content)
        if query_num > BaeMemcache.CACHE_MAX_QUERY_NUM:
            LOG.warning("BaeMemcache: '%s' failed: Query number must less than %d" % (cmd, BaeMemcache.CACHE_MAX_QUERY_NUM) )
            raise BaeMemcacheParamsError("Invalid Query number: %d" %query_num)
        query['content']['query_num'] = query_num
        i = 0
        for cont in content:
            qi = 'query%d' %i
            query['content'][qi] = {}
            query['content'][qi]['key'] = cont['key']
            if 'value' in cont:
                query['content'][qi]['value'] = cont['value']
            if 'delay_time' in cont:
                query['content'][qi]['delay_time'] = cont['delay_time']
            i += 1
        try:
            packq= mcpack.dumps(query)
            vars = {'log_id':query['logid'], 'body_len':len(packq)}
            nshead = self.nsh.pack_nshead(vars)
        except:
            LOG.exception('')
            raise BaeMemcacheInternalError("Failed to build valid query")
        return nshead + packq

    def __transf(self, cmd, buf):
        retry = 3
        while retry > 0:
            retry -= 1
            sock = self.__get_connection()
            if not sock:
                LOG.warning("BaeMemcache: '%s' failed: Connect with server failed. (retry %d)" % (cmd, retry) )
                continue
 
            sock.settimeout(6)
            try:
                sock.sendall(buf)
            except:
                LOG.warning("BaeMemcache: '%s' failed: Send request failed. (retry %d)" % (cmd, retry) )
                self.__close_connection()
                continue
                
            headbuf = ''
            count = 36
            while count > 0:
                d = sock.recv(count)
                if not d:
                    break
                headbuf += d
                count -= len(d)
            if count != 0:
                LOG.warning("BaeMemcache: '%s' failed: Recv response header failed: %d. (retry %d)" % (cmd, len(headbuf), retry) )
                self.__close_connection()
                continue

            try:
                nshead = self.nsh.unpack_nshead(headbuf)
            except:
                LOG.warning("BaeMemcache: '%s' failed: Parse response header failed." % cmd)
                raise BaeMemcacheInternalError('Parse response header failed.')

            mpbuf = ''
            count = nshead[6]
            while count > 0:
                d = sock.recv(count)
                if not d:
                    break
                mpbuf += d
                count -= len(d)

            if count != 0:
                LOG.warning("BaeMemcache: '%s' failed: Recv response body failed: %d. (retry %d)" % (cmd, len(mpbuf), retry) )
                self.__close_connection()
                continue
 
            try:
                ret = mcpack.loads(mpbuf)
            except:
                LOG.warning("BaeMemcache: '%s' failed: Parse response body failed." % cmd)
                raise BaeMemcacheInternalError('Parse response body failed.')
            return ret
        raise BaeMemcacheInternalError('Talk with server failed.')

    def __assertInput(self, cmd, key, value, time):
        if (key is not None and (not isinstance(key, str) or len(key) > BaeMemcache.CACHE_MAX_KEY_LEN)) or \
            (value is not None and len(value) > BaeMemcache.CACHE_MAX_VALUE_LEN) or \
            (time is not None and not isinstance(time, int)):
            LOG.warning("BaeMemcache: '%s' failed: Invalid params, check key/value/time" % cmd)
            raise BaeMemcacheParamsError('Invalid params, check key/value/time')

    def __strValue(self, value):
        if isinstance(value, int):
            val = '%d' % value
        elif isinstance(value, long):
            val = '%d' % value
        elif isinstance(value, str):
            tval = value.lstrip()
            if tval.isdigit() or (len(tval) > 0 and tval[0] == '-' and tval[1:].isdigit()):
                val = value
            else: val = pickle.dumps(value)
        else:
            val = pickle.dumps(value)
        return val
    
    def __unstrValue(self, value):
        tval = value.lstrip()
        if tval.isdigit() or (len(tval) > 0 and tval[0] == '-' and tval[1:].isdigit()):
            val = value
        else:
            val = pickle.loads(value)
        return val
 
    def __handleErr(self, cmd, ret, ext = None):
        errs =  False
        if ret['err_no'] != 0:
            LOG.warning("BaeMemcache: '%s' failed: Response is (%s)." % (cmd, str(ret)) )
            errs = True
        else:
            for i, err in ret['content'].items():
                if err['err_no'] != 0:
                    errs = True
                    if ext is not None:
                        ext.append(int(i[6:]))
            if errs:
                LOG.warning("BaeMemcache: '%s' failed: Response is (%s)" % (cmd, str(ret)) )
        return errs

    def setShareAppid(self, appid):
         if not isinstance(appid, str) or len(appid) > 64 or len(appid) <= 0:
            raise BaeMemcacheParamsError("Invalid appid")  
         self._appid = appid
         
    def set(self, key, value, time = 0, min_compress_len = 0):
        value = self.__strValue(value)
        self.__assertInput('set', key, value, time)
        buf = self.__buildQuery('set', [{'key':key, 'value':value, 'delay_time':time*1000}])
        ret = self.__transf('set', buf)
        return not self.__handleErr('set', ret)

    def get(self, key):
        self.__assertInput('get', key, None, None)
        buf = self.__buildQuery('get', [{'key':key}])
        ret = self.__transf('get', buf)
        if self.__handleErr('get', ret):
            return None
        try:
            return self.__unstrValue(ret['content']['result0']['value'])
        except KeyError:
            LOG.exception(str(ret))
            raise BaeMemcacheInternalError("Failed to receive complete data")
     
    def set_multi(self, mapping, time = 0, key_prefix = None, min_compress_len = 0):
        cont = []
        for k, v in mapping.items():
            v = self.__strValue(v)
            if key_prefix is not None:
                k = key_prefix + k
            self.__assertInput('set_multi', k, v, time)
            cont.append({'key':k, 'value':v, 'delay_time':time*1000})     
        buf = self.__buildQuery('set', cont)
        ret = self.__transf('set_multi', buf)
        errkeys = []    
        if self.__handleErr('set_multi', ret, errkeys):
            if errkeys == [] or len(errkeys) == len(mapping):
                return mapping.keys()
            else: 
                return [mapping.keys()[i] for i in errkeys]
        else:
            return []
    
    def get_multi(self, keys, key_prefix = None):
        pkeys = keys 
        if key_prefix is not None:
            pkeys =  map(lambda x: key_prefix+x, keys)
        cont = []
        for k in pkeys:
            self.__assertInput('get_multi', k, None, None)
            cont.append({'key':k})
        buf = self.__buildQuery('get', cont)
        ret = self.__transf('get_multi', buf)
        errkeys = []
        try:
            if self.__handleErr('get_multi', ret, errkeys):
                if errkeys == [] or len(errkeys) == len(keys):
                    return {}
                else:
                    _keys = [keys[i] for i in range(len(keys)) if i not in errkeys]
                    _results = ret['content'].keys()
                    _results.sort()
                    _vals = [ret['content'][i]['value'] for i in _results if int(i[6:]) not in errkeys]
                    _vals = map(self.__unstrValue, _vals)
                    return dict(zip(_keys, _vals))
            else:
                results = ret['content'].keys()
                results.sort()
                vals = [ret['content'][i]['value'] for i in results]
                vals = map(self.__unstrValue, vals)
                return dict(zip(keys, vals))
        except KeyError:
            LOG.exception(str(ret))
            raise BaeMemcacheInternalError("Failed to receive complete data")

    def add(self, key, value, time = 0, min_compress_len = 0):
        value = self.__strValue(value)
        self.__assertInput('add', key, value, time)
        buf = self.__buildQuery('add', [{'key':key, 'value':value, 'delay_time':time*1000}])
        ret = self.__transf('add', buf)
        return not self.__handleErr('add', ret)
    
    def replace(self, key, value, time = 0, min_compress_len = 0):
        value = self.__strValue(value)
        self.__assertInput('replace', key, value, time)
        buf = self.__buildQuery('replace', [{'key':key, 'value':value, 'delay_time':time*1000}])
        ret = self.__transf('replace', buf)
        return not self.__handleErr('replace', ret)

    def delete(self, key, time = 0):
        self.__assertInput('delete', key, None, time)
        buf = self.__buildQuery('delete', [{'key':key, 'delay_time':time*1000}])
        ret = self.__transf('delete', buf)
        return not self.__handleErr('delete', ret)

    def incr(self, key, delta = 1):
        if not isinstance(delta, int):
            LOG.warning("BaeMemcache: 'incr' failed: Delta must be a int")
            raise BaeMemcacheParamsError("Invalid delta type: ", type(delta))
        delta = str(delta)
        self.__assertInput('incr', key, delta, None)
        buf = self.__buildQuery('increment', [{'key':key, 'value':delta, 'delay_time':0}])
        ret = self.__transf('incr', buf)
        if self.__handleErr('incr', ret):
            return None
        try:
            return ret['content']['result0']['value']
        except KeyError:
            LOG.exception(str(ret))
            raise BaeMemcacheInternalError("Failed to receive complete data")

    def decr(self, key, delta = 1):
        if not isinstance(delta, int):
            LOG.warning("BaeMemcache: 'decr' failed: Delta must be a int")
            raise BaeMemcacheParamsError("Invalid delta type: ", type(delta))
        delta = str(delta)
        self.__assertInput('decr', key, delta, None)
        buf = self.__buildQuery('decrement', [{'key':key, 'value':delta, 'delay_time':0}])
        ret = self.__transf('decr', buf)
        if self.__handleErr('decr', ret):
            return None
        try:
            return ret['content']['result0']['value']
        except KeyError:
            LOG.exception(str(ret))
            raise BaeMemcacheInternalError("Failed to receive complete data")
