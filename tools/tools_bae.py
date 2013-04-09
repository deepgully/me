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

    from settings import BAE_BCMS
    ret = BAE_BCMS.createQueue("mail_queue")
    BcmsQueue = str(ret["response_params"]["queue_name"])
    BAE_BCMS.mail(BcmsQueue, body, address, fromaddr, subject, **kwargs)
    BAE_BCMS.dropQueue(BcmsQueue)


############################################
## Images
############################################
def save_file(binary, filename, public=True, mime_type="application/octet-stream"):
    today = datetime.now().strftime("%Y/%m/%d/")
    filename = today + filename

    from urlparse import urljoin
    from settings import BAE_BCS, BCS_HOST, BUCKET_NAME, BSC_FOLDER

    object_name = "%s%s" % (BSC_FOLDER, filename)
    err, resp = BAE_BCS.put_object(BUCKET_NAME, object_name, binary)
    if err != 0:
        raise Exception(resp)

    if public:
        #err, resp = BAE_BCS.make_public(BUCKET_NAME, object_name)
        acl_read = '{"statements":[{"action":["get_object"],"effect":"allow","resource":["%s%s"],"user":["*"]}]}' % (
            BUCKET_NAME, object_name)
        err, resp = BAE_BCS.set_acl(BUCKET_NAME, object_name, acl_read)
        if err != 0:
            BAE_BCS.del_object(BUCKET_NAME, object_name)
            raise Exception(resp)

    url = urljoin(BCS_HOST, BUCKET_NAME) + object_name
    return url, url


def delete_file(file_path):
    from urlparse import urlsplit
    from settings import BAE_BCS

    path = urlsplit(file_path).path
    _, bucket_name, object_name = path.split("/", 2)
    object_name = "/" + object_name

    err, resp = BAE_BCS.del_object(bucket_name, object_name)
    if err != 0:
        raise Exception(resp)



############################################
## memcache
############################################
from settings import ENABLE_MEMCACHE


if ENABLE_MEMCACHE:
    from bae.api.memcache import BaeMemcache

    memcache = BaeMemcache()  # bind memcache to BAE
    memcache.flush_all = lambda cls: None

