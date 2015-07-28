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
APIS of DataStore Layer
"""

from settings import app, logging


###########################################
## utils
###########################################
from operator import itemgetter
from itertools import groupby as _groupby


class _GroupTuple(tuple):
    __slots__ = ()
    grouper = property(itemgetter(0))
    list = property(itemgetter(1))

    def __new__(cls, (key, value)):
        return tuple.__new__(cls, (key, list(value)))


def make_getter(key):
    if key is None:
        return None
    if callable(key):
        return key

    if isinstance(key, basestring):
        groupers = key.split(",")

        def attrgetter(item):
            res = []
            for group in groupers:
                value = item
                attributes = group.strip().split('.')
                for part in attributes:
                    value = getattr(value, part.strip())
                res.append(value)
            return res if len(res) > 1 else res[0]

        return attrgetter


def group_by(items, key=None):
    keyfunc = make_getter(key)
    return map(_GroupTuple, _groupby(items, keyfunc))


###########################################
## DBAdapter
###########################################
class DBAdapter(object):
    def __init__(self, db_object=None):
        self.__dict__['db_object'] = db_object

    def __getattr__(self, attr):
        if attr == "db_object":
            self.__dict__['db_object'] = None
            return self.__dict__['db_object']
        return getattr(self.db_object, attr)

    def __setattr__(self, key, value):
        if key == "db_object":
            self.__dict__['db_object'] = value
        else:
            return setattr(self.db_object, key, value)

    def to_dict(self):
        return self.db_object.to_dict()


###########################################
## Settings
###########################################
from model import DBSiteSettings
from model import clean_cache


def get_site_settings():
    return DBSiteSettings.get_site_settings()


def clean_database_cache():
    clean_cache()


###########################################
## User
###########################################
from functools import wraps
from flask.ext.login import AnonymousUser
from flask.ext.login import UserMixin, current_user
from model import DBUser
from tools import secret_hash


class Anonymous(AnonymousUser):
    """
    This is the default object for representing an anonymous user.
    """
    is_admin = is_owner = is_user = lambda s: False

    @property
    def avatar(self):
        return ""


class User(UserMixin, DBAdapter):
    def __init__(self, dbuser=None):
        DBAdapter.__init__(self, dbuser)

    def is_active(self):
        return self.db_object.active

    def is_admin(self):
        return DBUser.UserRoles.index(self.role) >= DBUser.UserRoles.index("Admin")

    def is_owner(self):
        return DBUser.UserRoles.index(self.role) >= DBUser.UserRoles.index("Owner")

    def is_user(self):
        return self.db_object.active

    def update(self, **profile):
        if "password" in profile:
            if not 4 <= len(profile["password"].strip()) <= 30:
                raise Exception("password must be more than 4 and less than 30 characters")
            profile["password"] = secret_hash(profile["password"].strip(), salt=None)

        if "email" in profile:
            email = profile["email"].strip().lower()
            profile["email"] = email

            if self.email != email and User.check_exist(email=email):
                raise Exception("email address already exist")

        if "nickname" in profile:
            nickname = profile["nickname"].strip()
            profile["nickname"] = nickname
            if self.nickname != nickname and User.check_exist(nickname=nickname):
                raise Exception("nickname already exist")

        if "role" in profile:
            if profile["role"] not in DBUser.UserRoles:
                raise Exception("role must be in %s" % DBUser.UserRoles)

        self.db_object.update(**profile)

    @classmethod
    def create_user(cls, **settings):
        password = settings.pop("password")

        email = settings.pop("email").strip().lower()
        if User.check_exist(email=email):
            raise Exception("email address already exist")

        nickname = settings.get("nickname", "").strip()
        if User.check_exist(nickname=nickname):
            raise Exception("nickname already exist")

        dbuser = DBUser.create(email=email)
        dbuser.save()
        _ = dbuser.stats  # init stats
        dbuser.password = secret_hash(password, salt=None)
        dbuser.update(**settings)
        return cls(dbuser)

    @classmethod
    def check_exist(cls, **kwargs):
        return DBUser.check_exist(**kwargs)

    @classmethod
    def check_user(cls, email, password):
        dbuser = DBUser.get_user_by_email(email)
        if dbuser:
            if dbuser.password == secret_hash(password, salt=dbuser.password[:36]):
                return cls(dbuser)
            elif not dbuser.password:
                dbuser.update(password=secret_hash(app.config["DefaultPassword"], salt=None))

        return None

    @classmethod
    def get_by_id(cls, userid):
        dbuser = DBUser.get_by_id(userid)
        return dbuser and cls(dbuser)

    @classmethod
    def load_user(cls, userid):
        user = cls.get_by_id(userid)
        if user and user.is_active():
            return user
        return Anonymous()

    @classmethod
    def get_user_by_email(cls, email):
        dbuser = DBUser.get_user_by_email(email)
        return dbuser and cls(dbuser)

    @classmethod
    def get_current_user(cls):
        return current_user

    @classmethod
    def get_all_users(cls):
        return [cls(dbuser) for dbuser in DBUser.get_all()]

    @staticmethod
    def requires_site_owner(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if User.get_current_user().is_owner():
                return method(*args, **kwargs)
            raise Exception("unauthorized")
        return wrapper

    @staticmethod
    def requires_site_admin(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if User.get_current_user().is_admin():
                return method(*args, **kwargs)
            raise Exception("unauthorized")
        return wrapper

    @staticmethod
    def requires_site_user(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if User.get_current_user().is_user():
                return method(*args, **kwargs)
            raise Exception("unauthorized")
        return wrapper


###########################################
## Comment
###########################################
from model import DBComment


class Comment(DBAdapter):
    def __init__(self, dbcomment=None):
        DBAdapter.__init__(self, dbcomment)

    @classmethod
    def get_by_id(cls, id):
        dbcomment = DBComment.get_by_id(id)
        return dbcomment and cls(dbcomment)

    @classmethod
    def add_comment(cls, author, content, post_id, parent_id=-1):
        post = Post.get_by_id(post_id)
        if not post:
            raise Exception("no post %s" % post_id)
        parent_id = str(parent_id)
        post_id = str(post_id)
        dbcomment = DBComment.create(author=author, content=content,
            post_id=post.id, parent_id=parent_id)
        dbcomment.save()
        _ = dbcomment.stats  # init stats

        post.stats.increase("comment_count")
        post.category.stats.increase("comment_count")

        return cls(dbcomment)

    def delete(self, commit=True):
        self.deleted = True
        self.save()


###########################################
## Comment
###########################################
from model import DBPhoto
from tools import save_photo, delete_file


class Photo(DBAdapter):
    def __init__(self, dbphoto=None):
        DBAdapter.__init__(self, dbphoto)

    @classmethod
    def get_by_id(cls, id):
        dbphoto = DBPhoto.get_by_id(id)
        return dbphoto and cls(dbphoto)

    @classmethod
    def create_photo(cls, binary, **settings):
        url, real_file, url_thumb, real_file_thumb, mime = save_photo(binary)
        dbphoto = DBPhoto.create(url=url, mime=mime, real_file=real_file)
        dbphoto.url_thumb = url_thumb
        dbphoto.real_file_thumb = real_file_thumb
        dbphoto.save()
        _ = dbphoto.stats  # init stats
        photo = cls(dbphoto)
        photo.update(**settings)
        return photo

    @classmethod
    def create_photo_with_url(cls, url, real_file, mime,  **settings):
        dbphoto = DBPhoto.create(url=url, mime=mime, real_file=real_file)
        dbphoto.save()
        _ = dbphoto.stats  # init stats
        photo = cls(dbphoto)
        photo.update(**settings)
        return photo

    @classmethod
    def delete_file(cls, real_file, failsafe=True):
        try:
            delete_file(real_file)
        except:
            logging.exception("delete file error")
            if not failsafe:
                raise

    def delete(self, commit=True):
        post = Post.get_by_id(self.post_id)
        if post:
            post.stats.decrease("photo_count")
            post.category.stats.decrease("photo_count")

        Photo.delete_file(self.real_file)
        Photo.delete_file(self.real_file_thumb)
        self.db_object.delete(commit)

    def update(self, **settings):
        post_id = settings.get("post_id", None)
        if post_id is not None:
            if str(post_id) != str(self.post_id):
                old_post = Post.get_by_id(self.post_id)
                new_post = Post.get_by_id(post_id)
                if old_post:
                    old_post.stats.decrease("photo_count")
                    old_post.category.stats.decrease("photo_count")
                if new_post:
                    public = settings.get("public", new_post.public)
                    settings["public"] = public
                    new_post.stats.increase("photo_count")
                    new_post.category.stats.increase("photo_count")

            else:
                settings.pop("post_id")

        self.db_object.update(**settings)

    @classmethod
    def hot_photos(cls, count=12, order="like_count desc"):
        return DBPhoto.hot_photos(count, order)


###########################################
## Category
###########################################
from model import DBCategory


class Category(DBAdapter):
    def __init__(self, dbcategory=None):
        DBAdapter.__init__(self, dbcategory)

    def update(self, **settings):
        if "url" in settings:
            url = settings["url"].strip().lower()
            url = url.replace("/", "_")
            settings["url"] = url

        self.db_object.update(**settings)

    @classmethod
    def default_category(cls):
        category = DBCategory.get_by_url("")
        if not category:
            category = DBCategory.create(url="", name="Home")
            category.save()
            _ = category.stats  # init stats
        return cls(category)

    @classmethod
    def norm_url(cls, url):
        return url.replace("/", "_").strip().lower()

    @classmethod
    def create_category(cls, **settings):
        url = cls.norm_url(settings.pop("url"))
        name = settings.pop("name")
        if cls.check_exist(url=url):
            raise Exception("category %s exist" % url)
        dbcategory = DBCategory.create(url=url, name=name)
        dbcategory.save()
        _ = dbcategory.stats  # init stats
        dbcategory.update(**settings)
        return cls(dbcategory)

    @classmethod
    def get_by_id(cls, id):
        dbcategory = DBCategory.get_by_id(id)
        return dbcategory and cls(dbcategory)

    @classmethod
    def get_by_url(cls, category_url):
        if not category_url:
            return cls.default_category()
        category_url = cls.norm_url(category_url)
        dbcategory = DBCategory.get_by_url(category_url)
        return dbcategory and cls(dbcategory)

    @classmethod
    def check_exist(cls, **kwargs):
        return DBCategory.check_exist(**kwargs)

    def get_posts(self, page=1, per_page=10, include_no_published=False, start_cursor=""):
        return self.db_object.get_posts(page, per_page, include_no_published, start_cursor)

    def update(self, **settings):
        url = settings.get("url", None)
        if url is not None:
            url = Category.norm_url(url)
            category = DBCategory.get_by_url(url)
            if category and category.id != self.id:
                raise Exception("url '%s' exist" % url)
            settings["url"] = url

        self.db_object.update(**settings)


###########################################
## Post
###########################################
from model import DBPost


class Post(DBAdapter):
    def __init__(self, dbpost=None):
        DBAdapter.__init__(self, dbpost)

    @classmethod
    def get_by_id(cls, id):
        dbpost = id and DBPost.get_by_id(id)
        return dbpost and cls(dbpost)

    @classmethod
    def create_post(cls, author, category, **settings):
        dbpost = DBPost.create(author_id=author.db_object.id, category_id=category.db_object.id)
        dbpost.save()
        _ = dbpost.stats  # init stats
        author.stats.increase("post_count")
        category.stats.increase("post_count")
        post = cls(dbpost)
        post.update(**settings)
        return post

    @classmethod
    def hot_posts(cls, count=8, order="view_count desc"):
        return [cls(post) for post in DBPost.hot_posts(count, order)]

    @classmethod
    def latest_posts(cls, count=8, order="updated_date desc"):
        return [cls(post) for post in DBPost.latest_posts(count, order)]

    def update_photos(self, settings):
        public = settings.get("public", None)
        if "photos" in settings:
            photos = set(settings.pop("photos"))
            for photo_id in photos:
                photo = Photo.get_by_id(photo_id)
                if photo:
                    if public is None:
                        photo.update(post_id=self.id)
                    else:
                        photo.update(post_id=self.id, public=public)
        return settings

    def update_tags(self, settings):
        new_tags = settings.pop("tags", None)
        if new_tags is not None:
            new_tags = new_tags.split(",")
            new_tags = [tag.strip() for tag in list(set(new_tags)) if tag]
            old_tags = self.db_object.tags

            removed_tags = set(old_tags) - set(new_tags)
            for name in removed_tags:
                tag = Tag.get_tag_by_name(name)
                if tag:
                    tag.remove_post_id(self.id)
                    tag.save()

            added_tags = set(new_tags) - set(old_tags)
            for name in added_tags:
                tag = Tag.get_or_create(name)
                tag.add_post_id(self.id)
                tag.save()

            self.tags = new_tags
            self.save()
        return settings

    def update_category(self, settings):
        category_id = settings.get("category_id", None)
        if category_id is not None:
            if str(category_id) != str(self.category_id):
                old_category = Post.get_by_id(self.category_id)
                new_category = Post.get_by_id(category_id)
                if old_category:
                    old_category.stats.decrease("post_count")
                    old_category.stats.decrease("photo_count", self.stats.photo_count)
                    old_category.stats.decrease("comment_count", self.stats.comment_count)
                if new_category:
                    new_category.stats.increase("post_count")
                    new_category.stats.increase("photo_count", self.stats.photo_count)
                    new_category.stats.increase("comment_count", self.stats.comment_count)
            else:
                settings.pop("category_id")
        return settings

    def update(self, **settings):
        settings = self.update_photos(settings)

        settings = self.update_tags(settings)

        settings = self.update_category(settings)

        public = settings.get("public", None)
        self.db_object.update(**settings)
        if public is not None:
            for photo in self.db_object.photos:
                photo.update(public=public)

    def delete(self):
        for dbphoto in self.db_object.photos:
            Photo(dbphoto).delete(commit=False)

        comment_count = 0
        for dbcomment in self.db_object.Comments:
            dbcomment.delete(commit=False)
            comment_count += 1

        for tag_name in self.tags:
            tag = Tag.get_tag_by_name(tag_name)
            if tag:
                tag.remove_post_id(self.id)

        self.category.stats.decrease("comment_count", delta=comment_count, commit=False)
        self.category.stats.decrease("post_count", commit=False)
        self.author.stats.decrease("post_count", commit=False)

        self.db_object.delete(commit=True)

    @property
    def Comments(self):
        return [Comment(dbcomment) for dbcomment in self.db_object.Comments]

    @property
    def category(self):
        category = self.db_object.category
        if not category:
            category = Category.default_category()
            self.update_category({"category_id": category.id})

        return category

    @property
    def html(self):
        import markdown
        return markdown.markdown(self.body, safe_mode=False)

    @property
    def safe_html(self):
        import markdown
        return markdown.markdown(self.body, safe_mode=True)


###########################################
## Tag
###########################################
from model import DBTag


class Tag(DBAdapter):
    """
        Tag, only public posts
    """
    def __init__(self, dbtag=None):
        DBAdapter.__init__(self, dbtag)

    @classmethod
    def get_posts_by_name(cls, name, page=1, per_page=10):
        dbtag = DBTag.get_tag_by_name(name)
        if not dbtag:
            return []

        return [Post(dbpost) for dbpost in dbtag.get_posts(page, per_page)]

    @classmethod
    def hot_tags(cls, count=16):
        return [cls(dbtag) for dbtag in DBTag.hot_tags(count) if dbtag]

    @classmethod
    def get_or_create(cls, name):
        dbtag = DBTag.get_tag_by_name(name)
        if not dbtag:
            dbtag = DBTag.create(name)
        return cls(dbtag)

    @classmethod
    def get_tag_by_name(cls, name):
        dbtag = DBTag.get_tag_by_name(name)
        return dbtag and cls(dbtag)

    def get_posts(self, page=1, per_page=10):
        return [Post(dbpost) for dbpost in self.db_object.get_posts(page, per_page)]

    def add_post_id(self, post_id):
        self.db_object.add_post_id(post_id)

    def remove_post_id(self, post_id):
        self.db_object.remove_post_id(post_id)

###########################################
## Stats
###########################################
STATS_TYPES = ["Photo", "Post", "Comment"]
STATS_OPER = ["increase", "decrease"]


class Stats(object):
    @classmethod
    def stats(cls, stats_type, id, oper, name, delta=1):
        import apis
        if stats_type not in STATS_TYPES:
            raise Exception("stats_type must be in %s" % STATS_TYPES)
        if oper not in STATS_OPER:
            raise Exception("oper must be in %s" % STATS_OPER)

        stats = getattr(apis, stats_type).get_by_id(id).stats
        func = getattr(stats, oper)
        func(name, delta)
        return stats
