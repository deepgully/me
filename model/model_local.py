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

from settings import logging
import model_bae
from model_bae import *   # use same db model with BAE

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def init_database(app):
    settings = None
    try:
        settings = DBSiteSettings.get_by_id(1)

        if not settings or not settings.inited:
            raise Exception("Can not get site settings")

        if settings.version < DBSiteSettings.VERSION:
            raise Exception("Database expired")

    except:
        from alembic import command

        # auto generate alembic version in local
        try:
            command.revision(app.config["MIGRATE_CFG"],
                             "database v%s" % DBSiteSettings.VERSION,
                             True)
        except:
            logging.exception("migrate revision error")

        command.upgrade(app.config["MIGRATE_CFG"], "head")

        if not settings:
            settings = create_default_settings(app)
        else:
            settings.inited = True
            settings.version = DBSiteSettings.VERSION
            settings.save()

    app.config["SiteTitle"] = settings.title
    app.config["SiteSubTitle"] = settings.subtitle
    app.config["OwnerEmail"] = settings.owner

# inject local init_database function
model_bae.init_database = init_database
