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
import os

# import settings first to setup environment
from settings import app, RUNTIME_ENV
from settings import gettext

from flask import Response
from flask import request, g
from flask import redirect, url_for, flash, abort
from flask.helpers import safe_join
from werkzeug.contrib.atom import AtomFeed

import apis
from tools import unquote
from ajax import dispatch_action, jsonify, get_sitemap, get_latest_posts
from utils import render_template, get_locale, flask_render_template
from utils import login_required, login_user, logout_user

import model
app = model.bind_app(app)  # Bind DataBase Models


########################################
## Global Functions
########################################
def theme_file(theme, filename):
    filename = "themes/%s/%s" % (theme, filename)

    if RUNTIME_ENV not in ("gae", "gae_dev"):
        # GAE can not access static folder because the files will go to CDN instead of GAE instance
        real_file = safe_join(app.static_folder, filename)
        if not os.path.isfile(real_file):
            return ""

    return "%s/%s" % (app.static_url_path, filename)


@app.context_processor
def utility_processor():
    return {"theme_file": theme_file}


########################################
## Views
########################################
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=gettext("Page not found")), 404


@app.before_request
def before_request():
    g.locale = get_locale().replace("_", "-")


@app.route('/')
@app.route("/<path:category_url>", methods=['GET'])
def index(category_url=None):
    _category = None
    try:
        category_url = category_url and unquote(category_url)
        _category = apis.Category.get_by_url(category_url)
        if not _category:
            from ajax import MSG_NO_CATEGORY
            raise Exception(MSG_NO_CATEGORY % {'id': category_url})

        pager = {
            "cur_page": 0,
            "per_page": _category.posts_per_page,
            "group_by": "",
            "is_last_page": False,
        }
    except:
        abort(404)

    _category.stats.increase("view_count")
    return render_template("index.html", category=_category, pager = pager)


@app.route('/tags/<tag_name>', methods=['GET'])
def tags(tag_name):
    tag = None
    try:
        tag = apis.Tag.get_tag_by_name(unquote(tag_name))
        if not tag:
            from ajax import MSG_NO_TAG
            raise Exception(MSG_NO_TAG % {'name': tag_name})
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
        if not post:
            from ajax import MSG_NO_POST
            raise Exception(MSG_NO_POST % {"id": postid})

        if not post.public:
            user = apis.User.get_current_user()
            if not user.is_admin():
                raise Exception("not auth post %s" % postid)

    except Exception,e:
        from settings import logging
        logging.exception("post not found")
        abort(404)

    post.stats.increase("view_count")
    return render_template("post.html", post=post, category=post.category)


@app.route("/share")
def share():
    values = request.values
    postid = values.get("postid")
    if postid:
        url = url_for("post", postid=postid, _external=True)
    else:
        url = url_for("index", _external=True)
    title = values.get("title","").strip().replace("\n", " ")
    site = app.config["SiteTitle"].strip().replace("\n", " ")
    summary = values.get("summary", "").strip().replace("\n", " ")
    return flask_render_template("share.html", site=site, url=url, title=title, summary=summary)


@app.route('/json/<path:action>', methods=['GET', 'POST'])
def _json(action):
    return jsonify(dispatch_action(request.values, action))


@app.route("/sitemap.xml")
def sitemap():
    return Response(flask_render_template("sitemap.xml", sitemap=get_sitemap()), mimetype='text/xml')


@app.route("/atom")
@app.route("/feed")
def feed():

    _feed = AtomFeed(title=app.config["SiteTitle"],
                     subtitle=app.config["SiteSubTitle"],
                     icon=url_for("favicon", _external=True),
                     url=request.url_root)

    posts = get_latest_posts(12).get("posts", [])

    for _post in posts:
        _feed.add(title=_post.title,
                  content=_post.safe_html,
                  content_type='html',
                  author=_post.author.nickname,
                  url=url_for("post", postid=_post.id, _external=True),
                  updated=_post.updated_date,
                  published=_post.post_date)

    return Response(_feed.to_string(), mimetype='application/xml')


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

    return render_template("login.html", admin_page=True)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin", methods=['GET'])
@login_required
def admin():
    return render_template("admin.html",
                           admin_page=True,
                           users=apis.User.get_all_users())


# GAE blob store Serving
if RUNTIME_ENV in ("gae", "gae_dev"):
    import re
    from settings import BLOB_SERVING_URL, BLOB_UPLOAD_URL

    @app.route("%s/<blob_key>" % BLOB_SERVING_URL, methods=['GET'])
    def send_blob(blob_key):
        from flask import make_response
        from tools import make_blob_file_header

        blob_key = re.sub("(=s\d+)$", "", blob_key)

        headers = make_blob_file_header(blob_key)
        headers["Content-Type"] = "image/jpeg"
        headers["Cache-Control"] = "max-age=29030400, public"
        response = make_response()
        response.headers.extend(headers)
        return response

    def get_photo_url(blob_key):
        try:
            # get serving url for images
            from google.appengine.api import images
            url = images.get_serving_url(blob_key)
        except:
            url = "%s/%s" % (BLOB_SERVING_URL, str(blob_key))

        return url

    def get_blob_info_list(_request):
        if len(_request.files) == 0:
            raise Exception("no file uploaded")

        post_id = _request.values.get("post_id", "")
        blob_infos = []
        for key, value in _request.files.iteritems():
            if not isinstance(value, unicode):
                blob_key = value.mimetype_params["blob-key"]
                photo_url = get_photo_url(blob_key)
                blob_info = {
                    "real_file": blob_key,
                    "url": photo_url,
                    "mime": "image/jpeg",
                    "url_thumb": photo_url,
                    "real_file_thumb": blob_key,
                    "post_id": post_id,
                }
                blob_infos.append(blob_info)
        return blob_infos

    @app.route(BLOB_UPLOAD_URL, methods=['POST'])
    def upload_handler():
        result = {}
        try:
            blob_infos = get_blob_info_list(request)
            if not blob_infos:
                raise Exception("can not get blob info")

            photos = [apis.Photo.create_photo_with_url(**info) for info in blob_infos]
            result["status"] = "ok"
            result["photos"] = photos
        except Exception, e:
            from settings import logging
            logging.exception("error in upload_handler:")
            result["error"] = unicode(e)
            result["status"] = "error"

        return jsonify(result)


########################################
## Start Application
########################################
if RUNTIME_ENV == "bae":
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)

elif RUNTIME_ENV == "sae":
    import sae
    application = sae.create_wsgi_app(app)

elif RUNTIME_ENV == "local":
    application = app
    if __name__ == "__main__":
        app.run(debug=True)

elif RUNTIME_ENV in ("gae", "gae_dev"):
    application = app
