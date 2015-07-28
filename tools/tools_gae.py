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
def send_mail(body, address, fromaddr="", subject="", **kwargs):
    from google.appengine.api import mail
    from settings import app

    if not fromaddr:
        fromaddr = app.config["OwnerEmail"]

    mail.send_mail(sender=fromaddr, to=address, subject=subject, body=body, **kwargs)


############################################
## Images
############################################
def save_file(binary, filename, public=True, mime_type="application/octet-stream"):
    from google.appengine.api import files


    today = datetime.now().strftime("%Y_%m_%d_")
    filename = today + filename

    blob_file_name = files.blobstore.create(_blobinfo_uploaded_filename=filename)
    with files.open(blob_file_name, 'a') as f:
        f.write(binary)
    files.finalize(blob_file_name)
    blob_key = files.blobstore.get_blob_key(blob_file_name)

    try:
        # get serving url for images
        from google.appengine.api import images
        img = images.Image(binary)
        size = max(img.width, img.height)
        url = images.get_serving_url(blob_key, size=size)
    except:
        from settings import BLOB_SERVING_URL
        url = "%s/%s" %(BLOB_SERVING_URL, str(blob_key))

    return url, str(blob_key)


def delete_file(file_path):
    from google.appengine.ext import blobstore

    blobstore.delete(file_path)


def make_blob_file_header(blob_key_or_info, content_type=None, save_as=None):
    from google.appengine.ext import blobstore
    # Response headers.
    headers = {}

    if isinstance(blob_key_or_info, blobstore.BlobInfo):
        blob_key = blob_key_or_info.key()
        blob_info = blob_key_or_info
    else:
        blob_key = blob_key_or_info
        blob_info = None

    headers[blobstore.BLOB_KEY_HEADER] = str(blob_key)

    if content_type:
        if isinstance(content_type, unicode):
            content_type = content_type.encode('utf-8')

        headers['Content-Type'] = content_type
    else:
        if blob_info:
            headers['Content-Type'] = blob_info.content_type
        else:
            headers['Content-Type'] = ''

    def send_attachment(filename):
        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')

        headers['Content-Disposition'] = (
            'attachment; filename="%s"' % filename)

    if save_as:
        if isinstance(save_as, basestring):
            send_attachment(save_as)
        elif blob_info and save_as is True:
            send_attachment(blob_info.filename)
        else:
            if not blob_info:
                raise ValueError('Expected BlobInfo value for '
                    'blob_key_or_info.')
            else:
                raise ValueError('Unexpected value for save_as')
    return headers


############################################
## memcache
############################################
from settings import ENABLE_MEMCACHE


if ENABLE_MEMCACHE:
    from google.appengine.api import memcache as gae_memcache

    memcache = gae_memcache  # bind memcache to GAE
