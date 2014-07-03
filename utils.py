# -*- coding: utf-8 -*-
# Copyright 2013 (C) Gully Chen
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
Site utils interact with Flask request, response.
"""

from apis import Anonymous, User, get_site_settings

############################################
## common functions
############################################
from flask import render_template as flask_render_template


def render_template(template_name_or_list, **context):
    """add "user" and "settings" for every response"""
    context.update({
        "user": User.get_current_user(),
        "settings": get_site_settings(),
    })
    return flask_render_template(template_name_or_list, **context)


############################################
## Users
############################################
from settings import login_manager, lazy_gettext
from flask.ext.login import login_required, logout_user
from flask.ext.login import login_user as _login_user

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = lazy_gettext("Please login to access this page")


@login_manager.user_loader
def load_user(user_id):
    """flask.login user_loader callback"""
    return User.load_user(user_id)


def login_user(email, password, remember=False):
    """check and login user"""
    user = User.check_user(email, password)
    if user and user.is_active():
        _login_user(user, remember)
        return user
    return False


############################################
## i18n
############################################
from settings import babel
from flask import request
from translations.config import LANGUAGES


@babel.localeselector
def get_locale():
    """babel localeselector callback"""
    return request.accept_languages.best_match(LANGUAGES.keys()) or LANGUAGES.keys()[0]

