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
Site main views.
"""

# import settings first to setup environment
from settings import app, RUNTIME_ENV
from settings import gettext

import os

from flask import request, send_from_directory, g
from flask import redirect, url_for, flash, abort

import apis
from tools import unquote
from ajax import dispatch_action, jsonify, get_post
from utils import render_template, get_locale
from utils import login_required, login_user, logout_user

import model
app = model.bind_app(app)  # Bind DataBase Models


########################################
## Views
########################################
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=gettext("Page not found")), 404


@app.before_request
def before_request():
    g.locale = get_locale().replace("_", "-")


@app.route('/')
@app.route("/<path:category_url>", methods=['GET'])
def index(category_url=None):
    try:
        category_url = category_url and unquote(category_url)
        category = apis.Category.get_by_url(category_url)
        if not category:
            from ajax import MSG_NO_CATEGORY
            raise Exception(gettext(MSG_NO_CATEGORY, id=category_url))

        pager = {
            "cur_page": 0,
            "per_page": category.posts_per_page,
            "group_by": "",
            "is_last_page": False,
        }
    except:
        abort(404)

    category.stats.increase("view_count")
    return render_template("index.html", category=category, pager = pager)


@app.route('/tags/<tag_name>', methods=['GET'])
def tags(tag_name):
    try:
        tag = apis.Tag.get_tag_by_name(tag_name)
        if not tag:
            from ajax import MSG_NO_TAG
            raise Exception(gettext(MSG_NO_TAG, name=tag_name))
    except:
        abort(404)

    pager = {
        "cur_page": 0,
        "per_page": 10,
    }
    tag.stats.increase("view_count")
    return render_template("tags.html", tag=tag, pager=pager)


@app.route('/post/<postid>', methods=['GET'])
def post(postid):
    try:
        post = apis.Post.get_by_id(postid)
    except Exception,e:
        from settings import logging
        logging.exception("post not found")
        abort(404)
    post.stats.increase("view_count")
    return render_template("post.html", post=post, category=post.category)


@app.route('/json/<path:action>', methods=['GET', 'POST'])
def json(action):
    return jsonify(dispatch_action(request.values, action))


########################################
## Admin Views
########################################
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST" and "email" in request.form:
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        remember = request.form.get("remember", "no") != "no"

        if login_user(email, password, remember):
            return redirect(request.args.get("next") or url_for("index"))

        flash(gettext("Please input valid email and password"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin", methods=['GET'])
@login_required
def admin():
    return render_template("admin.html",
                           users=apis.User.get_all_users())


# GAE bolbstroe Serving
if RUNTIME_ENV in ("gae", "gae_dev"):
    from settings import BLOB_SERVING_URL

    @app.route("%s/<blob_key>" % BLOB_SERVING_URL, methods=['GET'])
    def send_blob(blob_key):
        from flask import make_response
        from tools import make_blob_file_header

        headers = make_blob_file_header(blob_key)
        headers["Content-Type"] = "image/jpeg"
        headers["Cache-Control"] = "max-age=29030400, public"
        response = make_response()
        response.headers.extend(headers)
        return response


########################################
## Start Application
########################################
if RUNTIME_ENV in ("bae",):
    from bae.middleware.profiler import ProfilingMiddleware
    application = ProfilingMiddleware(app)

    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(application)

elif RUNTIME_ENV in ("local",):
    app.run(debug=True)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    application = app
