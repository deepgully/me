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
"""
Site Settings for various runtime environments
"""


# Global Settings

import os
import sys


######################################
## Global environment
######################################

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "libs"))

try:
    from google.appengine.api import conf
    _, _, GAE_DEVELOPMENT = conf._inspect_environment()

    RUNTIME_ENV = "gae"
    if GAE_DEVELOPMENT:
        RUNTIME_ENV = "gae_dev"

    import logging
except:
    RUNTIME_ENV = "local"
    if "SERVER_SOFTWARE" in os.environ:
        from bae.core import const
        from bae.api import logging
        RUNTIME_ENV = "bae"
    else:
        import logging

from flask import Flask


######################################
## Application
######################################
app = Flask(__name__)

app.config["RUNTIME_ENV"] = RUNTIME_ENV

######################################
## Database
######################################
if RUNTIME_ENV in ("bae",):
    SAE_DATABASE = "qHWGMWtaVuVSNMEpprEk"

    app.secret_key = const.ACCESS_KEY + const.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (
        const.MYSQL_USER, const.MYSQL_PASS,
        const.MYSQL_HOST, const.MYSQL_PORT,
        SAE_DATABASE
        )
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 10
elif RUNTIME_ENV in ("local",):
    LOCAL_DATABASE = "test"

    app.secret_key = "ME@deepgully"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db'%LOCAL_DATABASE
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/%s'%LOCAL_DATABASE

elif RUNTIME_ENV in ("gae", "gae_dev"):

    app.secret_key = "ME@deepgully+GAE"


if RUNTIME_ENV in ("bae", "local"):
    from alembic.config import Config
    MIGRATE_CFG = Config("alembic.ini")
    MIGRATE_CFG.set_section_option("alembic", "sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['MIGRATE_CFG'] = MIGRATE_CFG


app.config["SiteTitle"] = "ME@deepgully"
app.config["SiteSubTitle"] = ""
app.config["OwnerEmail"] = "deepgully@gmail.com"
app.config["DefaultPassword"] = "admin"


######################################
## User
######################################
from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)


#####################################
## Mail
#####################################
if RUNTIME_ENV in ("bae",):
    from bae.api.bcms import BaeBcms

    BAE_BCMS = BaeBcms(const.ACCESS_KEY, const.SECRET_KEY)

elif RUNTIME_ENV in ("local",):
    app.config['MAIL_SERVER'] = "localhost"
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS '] = False
    app.config['MAIL_USE_SSL '] = False
    app.config['MAIL_USERNAME '] = "test"
    app.config['MAIL_PASSWORD '] = "test"

    from flask_mail import Mail
    mail = Mail(app)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    pass

#####################################
## Image Upload
#####################################
if RUNTIME_ENV in ("bae",):
    from bae.api import bcs

    BAE_BCS = bcs.BaeBCS(const.BCS_ADDR, const.ACCESS_KEY, const.SECRET_KEY)

    BCS_HOST = "http://bcs.duapp.com"
    BUCKET_NAME = "deepgully"
    BSC_FOLDER = "/photos/"

elif RUNTIME_ENV in ("local",):
    UPLOAD_URL = "static/uploads/"
    UPLOAD_FOLDER = os.path.join(app.root_path, UPLOAD_URL)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    BLOB_SERVING_URL = "/_files"
    app.config["BLOB_SERVING_URL"] = BLOB_SERVING_URL

THUMB_SIZE = (400, 300)

app.config["THUMB_SIZE"] = THUMB_SIZE


######################################
## i18n
######################################
from flask.ext.babel import Babel
from flask.ext.babel import gettext, lazy_gettext
_ = gettext
babel = Babel(app)


def T(string):
    """ fake function for babel """
    return string


######################################
## memcache
######################################
ENABLE_MEMCACHE = True
if RUNTIME_ENV in ("bae",):
    ENABLE_MEMCACHE = False  # default to disable memcache for BAE because it's not free

