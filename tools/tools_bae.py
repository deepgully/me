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

from datetime import datetime


############################################
## Mail
############################################
def send_mail(body, address, fromaddr=None, subject=None, **kwargs):
    if not isinstance(address, (list, tuple, set)):
        address = [address, ]

    #todo: support mail on BAE3
    raise NotImplemented


############################################
## Images
############################################
def save_file(binary, filename, public=True, mime_type="application/octet-stream"):
    today = datetime.now().strftime("%Y/%m/%d/")
    filename = today + filename

    from settings import BAE_BUCKET, const

    object_name = "%s%s" % (const.BSC_FOLDER, filename)

    bcs_obj = BAE_BUCKET.object(object_name)
    bcs_obj.put(binary)

    if public:
        bcs_obj.make_public()

    url = bcs_obj.public_get_url

    return url, url


def delete_file(file_path):
    from urlparse import urlsplit
    from settings import BAE_BCS

    path = urlsplit(file_path).path
    _, bucket_name, object_name = path.split("/", 2)
    object_name = "/" + object_name

    bucket = BAE_BCS.bucket(bucket_name)
    bcs_obj = bucket.object(object_name)
    bcs_obj.delete()


############################################
## memcache
############################################
from settings import const, ENABLE_MEMCACHE

if ENABLE_MEMCACHE:
    from bae_memcache.cache import BaeMemcache
    from tools import fail_safe_func

    # bind memcache to BAE
    memcache = BaeMemcache(const.CACHE_ID, const.CACHE_ADDR, const.CACHE_USER, const.CACHE_PASS)

    memcache.flush_all = lambda: None
    memcache.set = fail_safe_func(memcache.set)
