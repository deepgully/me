"""
The mcpack module
use dumps() and loads() to serialize/unserialize between python object
and mcpack data buffer

use version check mcpack version mcpackv1 or mcpackv2 default the _mcpack is mcpackv2

for low-level details, See public/mcpack and the implementation of
_mcpack module
"""

import _mcpack
mcpackv1 = 1
mcpackv2 = 2

_default_charset = 'gbk'
_default_buffer_size = 16 * 1024 * 1024
_default_tmp_size = 16 * 1024 *1024
_default_version = mcpackv2
_min_buff_size = 128

class Error(Exception): pass

def set_default_charset (charset):
    """Set the default charset in converting between unicode and str"""
    global _default_charset
    _default_charset = charset

def set_default_buffer_size (buffer_size):
    """
    Set the default mcpack buffer size when dumps(),
    it don't affect loads(), loads() assign buffer size automatically
    """
    global _default_buffer_size
    _default_buffer_size = buffer_size

def set_default_version (version):
    """
    set the default version to create mcpack
    """
    global _default_version
    if not (version >= mcpackv1 and version <= mcpackv2):
        raise Error, "only support mcpack.mcpackv1 and mcpack.mcpackv2"
    _default_version = version

class PackItem:
    """
    Create a pack item with certain type,
    avoiding automatically type detect when dumps()
    """
    
    def __init__ (self, item_type, item):
        self.item_type = item_type
        self.item = item

# Shortcuts
def INT32(item):
    """mcpack int32"""
    return PackItem('int32', item)
def UINT32(item):
    """mcpack uint32"""
    return PackItem('uint32', item)
def INT64(item):
    """mcpack int64"""
    return PackItem('int64', item)
def UINT64(item):
    """mcpack uint64"""
    return PackItem('uint64', item)
def RAW(item):
    """mcpack raw"""
    return PackItem('raw', item)
def STR(item):
    """mcpack str"""
    return PackItem('str', item)
def ARR(item):
    """mcpack arr"""
    return PackItem('arr', item)
def OBJ(item):
    """mcpack obj"""
    return PackItem('obj', item)
def FLOAT(item):
    """mcpack float"""
    return PackItem('float', item)
def DOUBLE(item):
    """mcpack double"""
    return PackItem('double', item)
def BOOLEAN(item):
    """mcpack bool"""
    return PackItem('boolean', item)
def NONE(item):
    """mcpack none"""
    return PackItem('none', item)



_UINT_BOUND	= 2 ** 31
_INT64_BOUND = 2 ** 32
_UINT64_BOUND	= 2 ** 63

def _detect_item_type(item):
    """
    Detect item type for the item
    """
    if (isinstance(item, bool)):
        return 'boolean';
    elif (isinstance(item, int)):
        if item >= _UINT64_BOUND:
            return 'uint64'
        elif item >= _INT64_BOUND:
            return 'int64'
        elif item >= _UINT_BOUND:
            return 'uint32'
        elif item > -_UINT_BOUND:
            return 'int32'
        return 'int64'
    elif (isinstance(item, long)):
        if item >= _UINT64_BOUND:
            return 'uint64'
        else:
            return 'int64'
    elif (isinstance(item, str) or isinstance(item, unicode)):
        return 'str'
    elif (isinstance(item, tuple) or isinstance(item, list)):
        return 'arr'
    elif (isinstance(item, dict)):
        return 'obj'
    elif (isinstance(item, type(None))):
        return 'none';
    elif (isinstance(item, float)):
        return 'double';
    else:
        raise Error, 'Unsupported python type [%s]' % (type(item),)    
    
def _dump_item (item, charset):
    """
    Covert python object into _mcpack item dict form
    """
    # use type information in PackItem or detect it automatically?
    if (isinstance(item, PackItem)):
        item_type = item.item_type
        item = item.item
    else:
        item_type = _detect_item_type(item)

    # dump item accroding to the item type
    if (item_type == 'int32' or item_type == 'uint32'):
        return (item_type, int(item))
    elif (item_type == 'int64' or item_type == 'uint64'):
        return (item_type, long(item))
    elif (item_type == 'double' or item_type == 'float'):
        return (item_type, float(item))
    elif (item_type == 'boolean'):
        return (item_type, bool(item))
    elif (item_type == 'none'):
        return (item_type, None)
    elif (item_type == 'str' or item_type == 'raw'):
        if (isinstance(item, unicode)):
            item = item.encode(charset)
        else:
            item = str(item)
        return (item_type, item)
    elif (item_type == 'arr'):
        return (
            item_type,
            map(lambda x: _dump_item(x, charset),
                item))
    elif (item_type == 'obj'):
        ret = {}
        for key, value in item.iteritems():
            ret[str(key)] = _dump_item(value, charset)
        return (item_type, ret)
    else:
        raise Error, 'Unsupported PackItem type [%s]' % (item_type,)
    
def _load_item (obj, use_unicode, charset):
    """
    covert _mcpack item dict form into python object
    """
    assert type(obj) is tuple, '_load_item obj should be tuple'
    assert len(obj) == 2, '_load_item obj should be a pair tuple'
    load_type, value = obj
    assert type(load_type) is str, 'the load_type should be str'

    if (load_type == 'int32' or load_type == 'uint32' or
        load_type == 'int64' or load_type == 'uint64' or
        load_type == 'raw' or load_type == 'float' or
        load_type == 'double' or load_type == 'none' or
        load_type == 'boolean'):
        return value
    elif (load_type == 'str'):
        if (use_unicode):
            return value.decode(charset)
        else:
            return value
    elif (load_type == 'arr'):
        assert type(value) is list, 'the value part of arr type should be list'
        return map(
            lambda x: _load_item(x, use_unicode, charset),
            value)
    elif (load_type == 'obj'):
        assert type(value) is dict, 'the value part of obj type should be dict'
        ret = {}
        for key, value in value.iteritems():
            if (use_unicode):
                key = key.decode(charset)
            ret[key] = _load_item(value, use_unicode, charset)
        return ret
    else:
        raise Error, 'Unsupported type [%s]' % (load_type,)

def dumps_version (version, item, buffer_size = None, charset = None, tmp_size = None):
    """
    dump python object into mcpack data buffer
    select a version
    """
    global _default_buffer_size, _default_charset
    buffer_size = buffer_size or _default_buffer_size
    buffer_size += _min_buff_size
    tmp_size = tmp_size or _default_tmp_size
    tmp_size += _min_buff_size
    charset = charset or _default_charset

    assert isinstance(item, dict), 'dumps() can only dump dict item'
    data = _dump_item(item, charset)
    if (data[0] != 'obj'):
        raise Error, 'cannot dump not-obj item to string'

    p = _mcpack.mcpack(version, buffer_size, tmp_size)
    for key, value in data[1].iteritems():
        p[key] = value
    p.pack()
    p.close()
    return p.getPack()

def dumps (item, buffer_size = None, charset = None, tmp_size = None):
    return dumps_version(_default_version,
            item,
            buffer_size,
            charset,
            tmp_size)

def loads (data, use_unicode = False, charset = None):
    """load python object from mcpack data buffer"""
    
    global _default_charset
    charset = charset or _default_charset
    
    p = _mcpack.mcpack(mcpackv1, len(data) + _min_buff_size,
            _default_tmp_size + _min_buff_size)
    """set Pack decide the mcpack version"""
    p.setPack(data)
    p.parse()
    return _load_item(('obj', p.getdict()),
                      use_unicode, charset)

def version (data):
    """get the mcpack data version"""
    return _mcpack.version(data)

def compack2mcpack(data,inc_mcpack_size_ratio=5):
    return _mcpack.compack2mcpack(data,len(data)*inc_mcpack_size_ratio)

    
