# -*- coding: utf-8 -*-
# Copyright 2014 Gully Chen
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

    #todo: support mail on SAE
    raise NotImplemented


############################################
## Images
############################################
def save_file(binary, filename, public=True, mime_type="application/octet-stream"):
    today = datetime.now().strftime("%Y/%m/%d/")
    filename = today + filename

    from settings import SAE_BUCKET, const

    folder = const.SAE_FOLDER[1:] if const.SAE_FOLDER.startswith("/") else const.SAE_FOLDER
    object_name = "%s%s" % (folder, filename)

    SAE_BUCKET.put_object(object_name, binary, mime_type)

    if public:
        SAE_BUCKET.post(acl=".r:*")

    url = SAE_BUCKET.generate_url(object_name)

    return url, url


def delete_file(file_path):
    from urlparse import urlsplit
    from sae.storage import Bucket

    res = urlsplit(file_path)

    hostname, path = res.hostname, res.path

    bucket_name = hostname.split(".", 1)[0].split("-")[-1]

    _, object_name = path.split("/", 1)

    bucket = Bucket(bucket_name)
    bucket.delete_object(object_name)


############################################
## memcache
############################################
from settings import ENABLE_MEMCACHE

if ENABLE_MEMCACHE:
    import pylibmc

    from tools import fail_safe_func

    memcache = pylibmc.Client()

    memcache.flush_all = fail_safe_func(memcache.flush_all)
    memcache.set = fail_safe_func(memcache.set)

