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
AJAX functions
"""

import re
import base64
from datetime import datetime

from flask import current_app, request, json, url_for

from settings import T, lazy_gettext, logging, RUNTIME_ENV
import apis

from tools import memcache

# Messages
MSG_NO_USER = T("can not find user %(id)s")
MSG_UNAUTHORIZED = T("unauthorized")
MSG_NO_CATEGORY = T("no category %(id)s")
MSG_ERROR_CATEGORY = T("error in get posts of category %(id)s")
MSG_NO_POST = T("no post %(id)s")
MSG_NO_PHOTO = T("no photo %(id)s")
MSG_NO_COMMENT = T("no comment %(id)s")
MSG_NO_TAG = T("no tag %(name)s")


# helper functions
def _get_method_doc(method_name):
    method = AJAX_METHODS.get(method_name)
    if method:
        return method.func_doc
    else:
        return lazy_gettext("unsupported method [ %(name)s]", name=method_name)


JSON_DATETIME_FORMAT = ["%Y-%m-%d",
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                        "%Y-%m-%dT%H:%M:%S.%f",
                        ]


def json_dumps(item):
    if hasattr(item, "to_dict"):
        return item.to_dict()

    if isinstance(item, datetime):
        return item.strftime(JSON_DATETIME_FORMAT[1])
    return item


def json_loads(date_str):
    if len(date_str) in [10, 19, 24, 26]:
        for format_str in JSON_DATETIME_FORMAT:
            try:
                return datetime.strptime(date_str, format_str)
            except:
                continue
    return date_str


def jsonify(*args, **kwargs):
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
                                                 default=json_dumps,
                                                 indent=None if request.is_xhr else 2),
                                      mimetype='application/json')


def format_key(fmt, *seq):
    res = fmt % seq
    if isinstance(res, unicode):
        res = res.encode("utf-8")
    return re.sub(r"\s", "_", res)


##############################################################
## API methods
##############################################################
def get_methods():
    """ return supported method list
    :return:
        methods: list(str), list of all supported methods
    """
    result = {"methods": [{"method_name": m, "method_doc": _get_method_doc(m)} for m in AJAX_METHODS.keys()],
              }
    return result


def get_method_info(method_name):
    """ return method's doc.
    Args:
        method_name: method name
    Returns:
        method_name: str, method name
        method_doc: str,  method's doc string
    """
    result = {"method_name": method_name,
              "method_doc": _get_method_doc(method_name),
              }
    return result


@apis.User.requires_site_owner
def update_site_settings(**settings):
    """update site settings.
    Args:
        settings: a dict of settings
    Returns:
        settings: a dict of settings"""
    dbsettings = apis.get_site_settings()

    # check setting values
    if "mirror_site" in settings:
        mirror_site = settings["mirror_site"]
        if not mirror_site:
            mirror_site = ""
        if not mirror_site.startswith("//") and not mirror_site.lower().startswith("http"):
            mirror_site = "//" + mirror_site

        mirror_site = mirror_site.rstrip("/")
        settings["mirror_site"] = mirror_site

    dbsettings.update(**settings)
    result = {
        "settings": dbsettings
    }
    return result


SITEMAP_CACHE_KEY = "SITEMAP_PAGES"
SITEMAP_CACHE_TIME = 3600*24*7   # cache 1 week


def get_sitemap():
    sitemap = memcache.get(SITEMAP_CACHE_KEY)
    if sitemap is None:
        sitemap = []
        for post in apis.Post.latest_posts(count=1000):
            sitemap.append({
                "loc": url_for("post", postid=post.id, _external=True),
                "lastmod": post.updated_date.strftime(JSON_DATETIME_FORMAT[0])
            })

        if sitemap:
            memcache.set(SITEMAP_CACHE_KEY, sitemap, SITEMAP_CACHE_TIME)

    return sitemap


@apis.User.requires_site_owner
def create_user(**settings):
    """create a new user.
    Args:
        settings: a dict of user settings
    Returns:
        user: a dict of user"""

    if "email" not in settings:
        raise Exception(lazy_gettext("email is required"))

    if "password" not in settings:
        raise Exception(lazy_gettext("password is required"))

    user = apis.User.create_user(**settings)

    result = {
        "user": user
    }
    return result


@apis.User.requires_site_user
def update_user_profile(id, **profile):
    """update user profile.
    Args:
        id: string of user id
        profile: a dict of user profile
    Returns:
        user: a dict of user profile"""

    user = apis.User.get_by_id(id)
    if not user:
        raise Exception(lazy_gettext(MSG_NO_USER, id=id))

    cur_user = apis.User.get_current_user()

    if cur_user.is_owner():
        pass
    elif user == cur_user:
        if "role" in profile:
            raise Exception(lazy_gettext(MSG_UNAUTHORIZED))
    else:
        raise Exception(lazy_gettext(MSG_UNAUTHORIZED))

    user.update(**profile)

    result = {
        "user": user
    }
    return result


@apis.User.requires_site_owner
def delete_user(id):
    """delete a user.
    Args:
        id: string of user id
    Returns:
        user: a dict of deleted user"""

    user = apis.User.get_by_id(id)
    if not user:
        raise Exception(lazy_gettext(MSG_NO_USER, id=id))

    if user.is_owner():
        raise Exception(lazy_gettext("can not delete owner"))

    result = {
        "user": user.to_dict(),
    }
    user.delete()

    return result


def get_category(id=None, url=None):
    """get category by id or url
    Args:
        id: category id
        url: category url
    Returns:
        category: a dict of category
    """
    if id is not None:
        category = apis.Category.get_by_id(id)
    elif url is not None:
        category = apis.Category.get_by_url(url)
    else:
        raise Exception(lazy_gettext("pls input id or url"))

    if not category:
        raise Exception(lazy_gettext(MSG_NO_CATEGORY, id=id))

    return {
        "category": category
    }


CATEGORY_CACHE_PAGES = 5  # cache first pages only
CATEGORY_CACHE_KEY = "category_id:%s_posts_page:%s_count:%s_public:%s"


def _delete_category_posts_cache(category):
    default_category = apis.Category.default_category()
    for page in range(CATEGORY_CACHE_PAGES+1):
        for public in (True, False):
            key = format_key(CATEGORY_CACHE_KEY, category.id, page, category.posts_per_page, public)
            memcache.delete(key)
            if category.id != default_category.id:
                key = format_key(CATEGORY_CACHE_KEY, default_category.id, page, default_category.posts_per_page, public)
                memcache.delete(key)


def get_posts_by_category(category="", page=1, per_page=10, group_by="", start_cursor=""):
    """get all posts of a category.
    Args:
        category: category id or url, if "", return all posts
        page: page number starts from 1
        per_page: item count per page
        start_cursor: GAE data store cursor
    Returns:
        pager: a pager
        posts: list of post"""

    try:
        if isinstance(category, int):
            category = get_category(id=category)["category"]
        else:
            category = get_category(url=category)["category"]
    except:
        raise Exception(lazy_gettext(MSG_ERROR_CATEGORY, id=category))

    if not category:
        raise Exception(lazy_gettext(MSG_NO_CATEGORY, id=category))

    cur_user = apis.User.get_current_user()
    get_no_published = cur_user.is_admin()

    result = {
        "pager": {
            "cur_page": page,
            "per_page": per_page,
            "group_by": group_by,
            "start_cursor": start_cursor,
        },
        "category": category,
    }

    if page <= CATEGORY_CACHE_PAGES:  # cache only CATEGORY_CACHE_PAGES pages
        key = format_key(CATEGORY_CACHE_KEY, category.id, page, per_page, get_no_published)
        res = memcache.get(key)

        if res is None:
            posts, end_cursor = category.get_posts(page, per_page, get_no_published, start_cursor)
            posts = [post.to_dict() for post in posts]
            memcache.set(key, (posts, end_cursor))
        else:
            posts, end_cursor = res
    else:
        posts, end_cursor = category.get_posts(page, per_page, get_no_published, start_cursor)

    result["posts"] = posts
    result["pager"]["start_cursor"] = end_cursor
    result["pager"]["is_last_page"] = len(posts) < per_page
    if group_by:
        result["group_posts"] = apis.group_by(posts, group_by)

    return result


@apis.User.requires_site_admin
def create_category(**settings):
    """create a new category.
    Args:
        settings: a dict of category settings
    Returns:
        category: a dict of category"""


    category = apis.Category.create_category(**settings)
    _delete_category_posts_cache(category)

    result = {
        "category": category
    }
    return result


@apis.User.requires_site_admin
def update_category(id, **settings):
    """update category settings.
    Args:
        id: string of category id
        settings: a dict of category settings
    Returns:
        category: a dict of category"""

    category = apis.Category.get_by_id(id)
    if not category:
        raise Exception(lazy_gettext(MSG_NO_CATEGORY, id=id))

    _delete_category_posts_cache(category)
    category.update(**settings)

    result = {
        "category": category
    }
    return result


@apis.User.requires_site_admin
def delete_category(id):
    """delete a category.
    Args:
        id: string of category id
    Returns:
        category: category id"""

    category = apis.Category.get_by_id(id)
    if not category:
        raise Exception(lazy_gettext(MSG_NO_CATEGORY, id=id))

    if category.url == "":
        raise Exception(lazy_gettext("can not delete Home category"))

    _delete_category_posts_cache(category)

    result = {
        "category": category.to_dict(),
    }
    category.delete()

    return result


@apis.User.requires_site_admin
def create_post(category_id=None, **settings):
    """create a new post in a category.
    Args:
        settings: a dict of post settings
    Returns:
        post: a dict of post"""

    category = apis.Category.get_by_id(category_id)
    if not category:
        category = apis.Category.default_category()

    _delete_category_posts_cache(category)
    memcache.delete(SITEMAP_CACHE_KEY)

    author = apis.User.get_current_user()

    post = apis.Post.create_post(author, category, **settings)

    _delete_post_cache(post)

    result = {
        "post": post
    }
    return result


POST_CACHE_KEY = "post_id:%s"


def _delete_post_cache(post):
    key = format_key(POST_CACHE_KEY, post.id)
    memcache.delete(key)


@apis.User.requires_site_admin
def update_post(id, **settings):
    """update a post.
    Args:
        id: post id
        settings: a dict of post settings
    Returns:
        post: a dict of post"""

    post = apis.Post.get_by_id(id)
    if not post:
        raise Exception(lazy_gettext(MSG_NO_POST, id=id))

    _delete_post_cache(post)
    _delete_category_posts_cache(post.category)

    post.update(**settings)

    _delete_category_posts_cache(post.category)

    result = {
        "post": post
    }
    return result

@apis.User.requires_site_admin
def delete_post(id):
    """delete a post.
    Args:
        id: post id
    Returns:
        post: a dict of post"""

    post = apis.Post.get_by_id(id)
    if not post:
        raise Exception(lazy_gettext(MSG_NO_POST, id=id))

    _delete_post_cache(post)
    _delete_category_posts_cache(post.category)

    result = {
        "post": post.to_dict(),
    }

    post.delete()

    return result


def get_post(id):
    """get a post.
    Args:
        id: post id
    Returns:
        post: a dict of post"""

    key = format_key(POST_CACHE_KEY, id)

    post = memcache.get(key)
    if post is None:
        post = apis.Post.get_by_id(id)
        if post:
            post = post.to_dict()
            memcache.set(key, post)

    if not post:
        raise Exception(lazy_gettext(MSG_NO_POST, id=id))

    if not post["public"]:
        cur_user = apis.User.get_current_user()
        if not cur_user.is_admin():
            raise Exception(lazy_gettext(MSG_UNAUTHORIZED))

    return {
        "post": post
    }


HOT_POSTS_CACHE_KEY = "HOT_POSTS_count:%s_order:%s"
HOT_POSTS_CACHE_TIME = 3600*24   # cache 1 day


def get_hot_posts(count=8, order="view_count desc"):
    """get hot posts.
    Args:
        count: post count
        order: hot order, default is "view_count desc"
    Returns:
        posts: a list of post"""

    key = format_key(HOT_POSTS_CACHE_KEY, count, order)
    posts = memcache.get(key)
    if posts is None:
        posts = apis.Post.hot_posts(count, order)
        if posts:
            memcache.set(key, posts, HOT_POSTS_CACHE_TIME)

    return {
        "posts": posts
    }


LATEST_POSTS_CACHE_KEY = "LATEST_POSTS_count:%s_order:%s"
LATEST_POSTS_CACHE_TIME = 3600*24   # cache 1 day


def get_latest_posts(count=12, order="updated_date desc"):
    """get latest posts.
    Args:
        count: post count
        order: posts order, default is "updated_date desc"
    Returns:
        posts: a list of post"""
    key = format_key(LATEST_POSTS_CACHE_KEY, count, order)
    posts = memcache.get(key)
    if posts is None:
        posts = apis.Post.latest_posts(count, order)
        if posts:
            memcache.set(key, posts, LATEST_POSTS_CACHE_TIME)

    return {
        "posts": posts
    }


COMMENT_CACHE_KEY = "comments_postid:%s"


def _delete_comments_cache(post_id):
    key = format_key(COMMENT_CACHE_KEY, post_id)
    memcache.delete(key)


def get_comments_by_post(id):
    """get comments by post.
    Args:
        id: post id
    Returns:
        comments: a list of comments"""
    post = apis.Post.get_by_id(id)
    if not post:
        raise Exception(lazy_gettext(MSG_NO_POST, id=id))

    key = format_key(COMMENT_CACHE_KEY, id)

    comments = memcache.get(key)
    if comments is None:
        comments = [comment.to_dict() for comment in post.Comments]
        memcache.set(key, comments)

    result = {
        "comments": comments
    }
    return result


def send_reset_mail(email):
    """send a reset mail
    Args:
        email: email address
    Returns:
        None
    """
    raise NotImplementedError("send_reset_mail not implemented")


@apis.User.requires_site_admin
def upload_photo(binary, **settings):
    """upload_photo a new photo.
    Args:
        binary: a base64 string of photo
        settings: settings of photo
    Returns:
        photo: a dict of photo"""

    binary = base64.b64decode(binary)

    photo = apis.Photo.create_photo(binary, **settings)

    result = {
        "photo": photo,
    }
    return result


@apis.User.requires_site_admin
def update_photo(id, **settings):
    """update a photo.
    Args:
        id: photo id
        settings: settings of photo
    Returns:
        photo: a dict of photo"""

    photo = apis.Photo.get_by_id(id)
    if not photo:
        raise Exception(lazy_gettext(MSG_NO_PHOTO, id=id))

    photo.update(**settings)

    result = {
        "photo": photo,
    }
    return result


@apis.User.requires_site_admin
def delete_photo(id):
    """date a photo.
    Args:
        id: photo id
    Returns:
        photo: a dict of photo"""

    photo = apis.Photo.get_by_id(id)
    if not photo:
        raise Exception(lazy_gettext(MSG_NO_PHOTO, id=id))

    result = {
        "photo": photo.to_dict(),
    }

    photo.delete()

    return result


def get_photo(id):
    """get photo by id.
    Args:
        id: photo id
    Returns:
        photo: photo"""
    photo = apis.Photo.get_by_id(id)
    if not photo:
        raise Exception(lazy_gettext(MSG_NO_PHOTO, id=id))

    return {
        "photo": photo
    }


def get_hot_photos(count=12, order="like_count desc"):
    """get hot photos.
    Args:
        count: photos count
        order: hot order, default is "view_count desc"
    Returns:
        photos: a list of photos"""

    return {
        "photos": apis.Photo.hot_photos(count, order)
    }


def get_comment(id):
    """get comment by id.
    Args:
        id: comment id
    Returns:
        comment: comment"""
    comment = apis.Comment.get_by_id(id)
    if not comment:
        raise Exception(lazy_gettext(MSG_NO_COMMENT, id=id))

    return {
        "comment": comment
    }


def create_comment(post_id, author, content, parent_id=-1):
    """create a new comment in a post.
    Args:
        post_id: id of post
        author: author name
        content: content
    Returns:
        comment: comment"""

    post = apis.Post.get_by_id(post_id)
    if not post:
        raise Exception(lazy_gettext(MSG_NO_POST, id=post_id))

    comment = apis.Comment.add_comment(author, content, post_id, parent_id)

    _delete_comments_cache(post_id)

    result = {
        "comment": comment
    }
    return result


@apis.User.requires_site_admin
def update_comment(id, **settings):
    """date a comment.
    Args:
        id: comment id
        settings: dict of comment settings
    Returns:
        comment: a dict of comment"""
    comment = apis.Comment.get_by_id(id)
    if not comment:
        raise Exception(lazy_gettext(MSG_NO_COMMENT, id=id))

    _delete_comments_cache(comment.post_id)
    comment.update(**settings)
    _delete_comments_cache(comment.post_id)

    result = {
        "comment": comment,
    }
    return result


@apis.User.requires_site_admin
def delete_comment(id):
    """date a comment.
    Args:
        id: comment id
    Returns:
        comment: a dict of comment"""
    comment = apis.Comment.get_by_id(id)
    if not comment:
        raise Exception(lazy_gettext(MSG_NO_COMMENT, id=id))

    _delete_comments_cache(comment.post_id)

    comment.delete()

    result = {
        "comment": comment,
    }

    return result


TAG_POSTS_CACHE_KEY = "tag_posts_name:%s_page:%s_per_page:%s"


def get_posts_by_tag(name, page=1, per_page=10):
    """get posts by tag.
    Args:
        name: tag name
        page: page number, starts with 1
        per_page: post count per page
    Returns:
        tag: a tag
        pager: a pager
        posts: a list of posts"""

    tag = apis.Tag.get_tag_by_name(name)
    if not tag:
        raise Exception(lazy_gettext(MSG_NO_TAG, name=name))

    key = format_key(TAG_POSTS_CACHE_KEY, tag.name, page, per_page)

    posts = memcache.get(key)
    if posts is None:
        posts = [post.to_dict() for post in tag.get_posts(page, per_page)]
        memcache.set(key, posts, 3600)  # cache 1 hour

    result = {
        "tag": tag.to_dict(),
        "pager": {
            "cur_page": page,
            "per_page": per_page,
            "is_last_page": len(posts) < per_page
        },
        "posts": posts
    }

    return result


HOT_TAGS_CACHE_KEY = "hot_tags_count:%s"


def get_hot_tags(count=12):
    """get hot tags.
    Args:
        count: tags count
    Returns:
        tags: a list of tags"""


    key = format_key(HOT_TAGS_CACHE_KEY, count)

    tags = memcache.get(key)
    if tags is None:
        tags = apis.Tag.hot_tags(count)
        memcache.set(key, tags, 3600*24)  # cache 24 hour

    return {
        "tags": apis.Tag.hot_tags(count)
    }


def stats(stats_type, id, oper, name, delta=1):
    """ increase stats unlike_count.
    Args:
        stats_type: stats type in ["Photo", "Post", "Comment"]
        id: item id
        oper: operation in ["increase", "decrease"]
        name: stats name
    Returns:
        stats: new stats"""

    stats = apis.Stats.stats(stats_type, id, oper, name, delta)

    result = {
        "stats": stats,
    }

    return result


###########################################
## Admin functions
###########################################
@apis.User.requires_site_owner
def admin_memcache(action, params={}):
    """ memcache functions.
    Args:
        action: memcache action
        params: function params
    Returns:
        result: function result"""
    apis.clean_database_cache()
    function = getattr(memcache, action)
    if callable(function):
        result = function(**params)
    else:
        raise Exception("wrong memcache action")

    return {
        "result": result,
    }


# define all methods
AJAX_METHODS = {
    "methods": get_methods,
    "method/info": get_method_info,
    "site_settings/update": update_site_settings,
    "reset_mail/send": send_reset_mail,
    "user/create": create_user,
    "user/update": update_user_profile,
    "user/delete": delete_user,
    "category": get_category,
    "category/create": create_category,
    "category/update": update_category,
    "category/delete": delete_category,
    "category/posts": get_posts_by_category,
    "post": get_post,
    "posts/hot": get_hot_posts,
    "posts/latest": get_latest_posts,
    "post/create": create_post,
    "post/update": update_post,
    "post/delete": delete_post,
    "post/comments": get_comments_by_post,
    "photo": get_photo,
    "photos/hot": get_hot_photos,
    "photo/upload": upload_photo,
    "photo/update": update_photo,
    "photo/delete": delete_photo,
    "comment": get_comment,
    "comment/create": create_comment,
    "comment/update": update_comment,
    "comment/delete": delete_comment,
    "tag/posts": get_posts_by_tag,
    "tags/hot": get_hot_tags,
    "stats": stats,
    # Admin functions
    "admin/memcache": admin_memcache,
}

ERROR_RES = {"status": "error",
             "error": "",
             "response": {},
             }


def dispatch_action(parameters, action):
    result = ERROR_RES.copy()
    try:
        parameters = parameters.to_dict()
        method = AJAX_METHODS.get(action)
        if method:
            for key in parameters:
                val = json.loads(parameters[key])
                if isinstance(val, basestring):
                    val = json_loads(val)
                parameters[key] = val
            res = method(**parameters)
            result["status"] = "ok"
            result["response"] = res
        else:
            result["status"] = "error"
            result["error"] = format_key("unsupported method [%s]", action)

    except Exception, e:
        logging.exception("Error in dispatch_action:")
        result["error"] = unicode(e)
        result["status"] = "error"
    return result


# GAE Files API was deprecated, use blobstore
if RUNTIME_ENV in ("gae", "gae_dev"):
    from settings import BLOB_UPLOAD_URL
    from google.appengine.ext import blobstore

    @apis.User.requires_site_admin
    def get_upload_url():
        upload_url = blobstore.create_upload_url(BLOB_UPLOAD_URL)
        return {
            "upload_url": upload_url
        }

    AJAX_METHODS["photo/upload_url"] = get_upload_url
