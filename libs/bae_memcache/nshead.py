import struct

class NsheadException(Exception):
    pass

class CNsHead(object):
    def __init__(self):
        self.orig = {
             'id' : 0,
             'version' : 0,
             'log_id' : 0,
             'provider' : 'zcacheadapter',
             'magic_num' : 0xfb709394,
             'reserved' : 0,
             'body_len' : 0}

    def pack_nshead(self, vars):
        for key, value in vars.items():
            self.orig[key] = value
        try:
            nshead = struct.pack('HHI16sIII', self.orig['id'], self.orig['version'], self.orig['log_id'], self.orig['provider'], 
                             self.orig['magic_num'], self.orig['reserved'], self.orig['body_len']) 
            return nshead
        except Exception, e:
            raise NsheadException(e.__str__())

    def unpack_nshead(self, nshead):
        try:
            ret = struct.unpack('HHI16sIII', nshead)
            return ret
        except Exception, e:
            raise NsheadException(e.__str__())



