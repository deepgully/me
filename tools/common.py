# -*- coding: utf-8 -*-
# Copyright 2013 Gully Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
from hmac import HMAC
from hashlib import sha256
from functools import wraps

from urllib import unquote as _unquote

from settings import app, logging, QINIU_SETTINGS


############################################
## common functions
############################################
def secret_hash(source, salt=None, key=app.secret_key):
    if salt is None:
        salt = str(uuid.uuid4())
    if isinstance(source, unicode):
        source = source.encode("utf-8")
    result = source + key
    for i in xrange(8):
        result = HMAC(result, salt, sha256).hexdigest()
    return salt + result


def unquote(s):
    return unicode(_unquote(s.encode("utf-8")), "utf-8")


def fail_safe_func(func, fail_safe=True):
    @wraps(func)
    def fail_safe(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logging.exception("error in func call [%s]" % func.__name__)
            if not fail_safe:
                raise

    return fail_safe


############################################
## Images
############################################
class ImageMime:
    GIF = "image/gif"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    PNG = "image/png"
    BMP = "image/bmp"
    ICO = "image/x-icon"
    UNKNOWN = "application/octet-stream"


def get_img_type(binary):
    size = len(binary)
    if size >= 6 and binary.startswith("GIF"):
        return ImageMime.GIF, ".gif"
    elif size >= 8 and binary.startswith("\x89PNG\x0D\x0A\x1A\x0A"):
        return ImageMime.PNG, ".png"
    elif size >= 2 and binary.startswith("\xff\xD8"):
        return ImageMime.JPEG, ".jpg"
    elif (size >= 8 and (binary.startswith("II\x2a\x00") or
                             binary.startswith("MM\x00\x2a"))):
        return ImageMime.TIFF, ".tif"
    elif size >= 2 and binary.startswith("BM"):
        return ImageMime.BMP, ".bmp"
    elif size >= 4 and binary.startswith("\x00\x00\x01\x00"):
        return ImageMime.ICO, ".ico"
    else:
        return ImageMime.UNKNOWN, ""


if QINIU_SETTINGS.Enabled:
    from datetime import datetime
    from qiniu import io, rs, fop, conf
    from settings import THUMB_SIZE

    conf.ACCESS_KEY = QINIU_SETTINGS.ACCESS_KEY
    conf.SECRET_KEY = QINIU_SETTINGS.SECRET_KEY

    def save_file_qiniu(binary, filename, mime="application/octet-stream"):

        today = datetime.now().strftime("%Y/%m/%d/")
        filename = today + filename

        policy = rs.PutPolicy(QINIU_SETTINGS.BUCKET_NAME)
        uptoken = policy.token()

        extra = io.PutExtra()
        extra.mime_type = mime

        res, err = io.put(uptoken, filename, binary, extra)
        if err is not None:
            raise Exception("Qiniu save file [%s] error: %s res: %s" % (filename, err, res))

        url = rs.make_base_url(QINIU_SETTINGS.BUCKET_DOMAIN, filename)

        iv = fop.ImageView()
        iv.mode = 2
        iv.width = THUMB_SIZE[0]
        url_thumb = iv.make_request(url)

        return url, url_thumb

    def delete_file_qiniu(file_path):
        from urlparse import urlsplit

        res = urlsplit(file_path)

        hostname, path, query_str = res.hostname, res.path, res.query

        if query_str.strip():
            return  # can not delete fop url

        bucket, host = hostname.split(".", 1)   # assume it's qiniu sub-domain

        if host.lower() != "qiniudn.com":   # it's not qiniu domain
            if hostname.lower() != QINIU_SETTINGS.BUCKET_DOMAIN.lower():
                raise Exception("can not delete file not in domain %s" % QINIU_SETTINGS.BUCKET_DOMAIN)

            # it's same domain, use bucket in settings
            bucket = QINIU_SETTINGS.BUCKET_NAME

        _, key = path.split("/", 1)

        ret, err = rs.Client().delete(bucket, key)
        if err is not None:
            raise Exception("Qiniu delete file [%s] error: %s res: %s" % (file_path, err, res))


def save_photo(binary):
    mime, ext = get_img_type(binary)
    if mime == ImageMime.UNKNOWN:
        raise Exception("unsupported image format")

    rand_str = str(uuid.uuid1())
    filename = rand_str + ext

    if QINIU_SETTINGS.Enabled:
        url, url_thumb = save_file_qiniu(binary, filename, mime)

        return url, url, url_thumb, url_thumb, mime

    else:
        from tools import save_file

        url, real_file = save_file(binary, filename, mime_type=mime)

        url_thumb = real_file_thumb = ""
        try:
            import StringIO

            from PIL import Image
            from settings import THUMB_SIZE

            im = Image.open(StringIO.StringIO(binary))
            im.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

            thumb = StringIO.StringIO()
            thumb.name = filename
            im.save(thumb)
            binary = thumb.getvalue()
            thumb.close()

            mime, ext = get_img_type(binary)
            thumb_filename = rand_str + "_thumb" + ext

            url_thumb, real_file_thumb = save_file(binary, thumb_filename, mime_type=mime)
        except:
            logging.exception("save thumb error")

        return url, real_file, url_thumb, real_file_thumb, mime


######################################
## memcache
######################################
from time import time as sys_time
try:
    import cPickle as pickle
except ImportError:
    import pickle


class memcache():
    """ Dummy memcache class for compatibility
    """
    mem_cache = {}
    MAX_ITEMS = 500
    DEFAULT_TIMEOUT = 3600 * 24

    @classmethod
    def _prune(cls):
        if len(cls.mem_cache) > cls.MAX_ITEMS:
            now = sys_time()
            for idx, (key, (expires, _)) in enumerate(cls.mem_cache.items()):
                if expires <= now or idx % 3 == 0:
                    cls.mem_cache.pop(key, None)

    @classmethod
    def get(cls, key):
        expires, value = cls.mem_cache.get(key, (0, None))
        if expires > sys_time():
            return pickle.loads(value)
        return None

    @classmethod
    def get_multi(cls, keys, key_prefix=None):
        res = {}
        for key in keys:
            if key_prefix is not None:
                key = key_prefix + key

            res[key] = cls.get(key)
        return res

    @classmethod
    def set(cls, key, value, time=None, min_compress_len=0):
        if time is None:
            time = cls.DEFAULT_TIMEOUT

        cls._prune()
        cls.mem_cache[key] = (sys_time() + time, pickle.dumps(value,
                                                          pickle.HIGHEST_PROTOCOL))
        return True

    @classmethod
    def set_multi(cls, mapping, time=None, key_prefix=None, min_compress_len=0):
        res = []
        for _key, value in mapping.iteritems():
            if key_prefix is None:
                key = _key
            else:
                key = key_prefix + _key

            if not cls.set(key, value, time, min_compress_len):
                res.append(_key)

        return res

    @classmethod
    def replace(cls, key, value, time=None, min_compress_len=0):
        return cls.set(key, value, time, min_compress_len)

    @classmethod
    def incr(cls, key, delta=1):
        try:
            value = cls.get(key)
            value += delta
            cls.set(key, value)
            return value
        except:
            cls.set(key, delta)
            return None

    @classmethod
    def decr(cls, key, delta=1):
        try:
            value = cls.gt(key)
            value -= delta
            cls.set(key, value)
            return value
        except:
            cls.set(key, delta)
            return None

    @classmethod
    def delete(cls, key, time=None):
        res = cls.mem_cache.pop(key, False)
        return res

    @classmethod
    def flush_all(cls):
        cls.mem_cache.clear()


