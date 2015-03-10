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

import os
from datetime import datetime


############################################
# Mail
############################################
def send_mail(body, address, fromaddr=None, subject=None, **kwargs):
    if not isinstance(address, (list, tuple, set)):
        address = [address, ]

    from settings import mail
    from flask_mail import Message
    msg = Message(subject, sender=fromaddr, recipients=address, body = body)
    mail.send(msg)


############################################
# Images
############################################
def save_file(binary, filename, public=True, mime_type="application/octet-stream"):
    today = datetime.now().strftime("%Y/%m/%d/")
    filename = today + filename

    from settings import UPLOAD_FOLDER, UPLOAD_URL

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    folder = os.path.dirname(file_path)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f = open(file_path, "wb")
    f.write(binary)
    f.close()

    url = "/%s%s" % (UPLOAD_URL, filename)
    return url, file_path


def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)


############################################
# memcache
############################################
from settings import app, ENABLE_MEMCACHE

if ENABLE_MEMCACHE:
    try:
        import memcache as memcache_lib
        mc_client = memcache_lib.Client(app.config['MEMCACHE_SERVERS'])
        if mc_client.set("me_memcache_testing", ""):
            memcache = mc_client
    except:
        # can not init memcache server, use dummy memcache on local
        pass

