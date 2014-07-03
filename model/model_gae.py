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

import hashlib

from settings import logging
from google.appengine.ext import db
from google.appengine.api import datastore

import common


def bind_app(app):
    init_database(app)
    app.teardown_request(clean_cache)
    return app


def create_default_settings(app):
    title = app.config["SiteTitle"]

    from apis import User, Post, Category
    home = Category.default_category()

    owner = User.get_user_by_email(app.config["OwnerEmail"])
    if not owner:
        owner = User.create_user(email=app.config["OwnerEmail"],
                                 password=app.config["DefaultPassword"],
                                 role="Owner")

    Post.create_post(owner, home, title=common.Welcome_Title % title,
        body=common.Welcome_Post % title)

    settings = DBSiteSettings.create_settings(title=title, inited=True,
                                              subtitle=app.config["SiteSubTitle"],
                                              owner=app.config["OwnerEmail"],
                                              version=DBSiteSettings.VERSION)
    settings.save()
    return settings


def init_database(app):

    settings = DBSiteSettings.get_site_settings()
    if settings is None:
        settings = create_default_settings(app)
    if settings.version < DBSiteSettings.VERSION:
        settings.version = DBSiteSettings.VERSION
        settings.save()

    app.config["SiteTitle"] = settings.title
    app.config["SiteSubTitle"] = settings.subtitle
    app.config["OwnerEmail"] = settings.owner


def gae_order(str_order):
    parts = str_order.split(" ", 2)
    if len(parts) == 1:
        return str_order

    name, order = parts
    if order == "asc":
        return name
    elif order == "desc":
        return "-" + name
    else:
        return name


def gae_type_convert(val, target_type):
    if not isinstance(val, target_type):
        if target_type == list and isinstance(val, basestring):
            val = [line.strip() for line in val.strip().split("\n") if (line and line.strip())]
        elif target_type == bool and isinstance(val, basestring):
            val = val.strip().capitalize()
            if val == "False" or val == u"False":
                val = False
            else:
                val = True
        elif target_type == basestring:
            try:
                val = str(val)
            except:
                val = unicode(val)
        else:
            try:
                val = target_type(val)
            except:
                pass

    return val

# DataStore Cache in Memory
__db_get_cache = {}


def clean_cache(*args, **kwargs):
    __db_get_cache.clear()


def get(keys, **kwargs):
    keys, multiple = datastore.NormalizeAndTypeCheckKeys(keys)
    ret = db.get([key for key in keys if key not in __db_get_cache], **kwargs)
    if (len(ret) == 1) and (ret[0] is None) and (not multiple):
        return
    __db_get_cache.update(dict([(x.key(), x) for x in ret if x is not None]))
    ret = [__db_get_cache.get(k, None) for k in keys]
    if multiple:
        return ret
    if len(ret) > 0:
        return ret[0]


def remove(keys):
    keys, _ = datastore.NormalizeAndTypeCheckKeys(keys)
    return [__db_get_cache.pop(k) for k in keys if k in __db_get_cache]


class DBParent(db.Model):
    pass

BASEMODEL_PARENT = DBParent.get_or_insert("DBParent_basemodel_parent")


class BaseModel(db.Model):
    db_parent = BASEMODEL_PARENT
    protect_attrs = []
    additional_attrs = []

    @classmethod
    def create(cls, **kwargs):
        return BaseModel._create(cls, **kwargs)

    @staticmethod
    def _create(cls, **kwargs):
        parent = BASEMODEL_PARENT
        return cls(parent, **kwargs)

    @property
    def str_key(self):
        return str(self.key())

    @property
    def id(self):
        return str(self.key().id())

    @property
    def key_name(self):
        return self.key().name()

    def to_dict(self):
        _res = {}
        if hasattr(self, "stats"):
            _res["stats"] = self.stats.to_dict()
        _res["id"] = str(self.id)

        props = self.properties()
        res = dict([(k, getattr(self, k)) for k in props.keys() if
                    (not k.startswith("_") and k not in self.protect_attrs)])

        res.update(_res)
        return res

    def update(self, commit=True, **kwargs):
        props = self.properties()
        need_save = False
        for attr, val in kwargs.iteritems():
            if getattr(self, attr, None) != val:
                if (not attr.startswith("_")) and (attr != "id"):
                    if (attr in props) or (unicode(attr) in props) or attr in self.additional_attrs:
                        need_save = True
                        val = gae_type_convert(val, props[attr].data_type)
                        setattr(self, attr, val)
                        if attr == "public" and hasattr(self, "stats"):
                            self.stats.public = val
                            self.stats.save()

        if need_save:
            self.save()
        return self

    def put(self):
        count = 0
        while count < 3:
            try:
                ret = db.Model.put(self)
                if ret:
                    break
            except db.Timeout:
                count += 1
        else:
            raise db.Timeout()
        remove(self.key())
        return ret

    def save(self, commit=True):
        return self.put()

    def delete(self, commit=False):
        keys = [self.key()]
        if hasattr(self, "stats"):
            keys.append(self.stats.key())
        remove(keys)
        return db.delete(keys)

    @classmethod
    def get_by_key_name(cls, key_names, parent=None, **kwargs):
        try:
            if not parent:
                parent = cls.db_parent
            parent = db._coerce_to_key(parent)
        except db.BadKeyError, e:
            raise db.BadArgumentError(str(e))
        rpc = datastore.GetRpcFromKwargs(kwargs)
        key_names, multiple = datastore.NormalizeAndTypeCheck(key_names, basestring)
        keys = [datastore.Key.from_path(cls.kind(), name, parent=parent)
                for name in key_names]
        if multiple:
            return get(keys, rpc=rpc)
        else:
            return get(keys[0], rpc=rpc)

    @classmethod
    def get_by_id(cls, ids, parent=None, **kwargs):
        if not parent:
            parent = cls.db_parent
        rpc = datastore.GetRpcFromKwargs(kwargs)
        if isinstance(parent, db.Model):
            parent = parent.key()

        if ids is None:
            return None

        if isinstance(ids, (list, tuple, set)):
            ids = [long(id) for id in ids]
        else:
            ids = long(ids)

        ids, multiple = datastore.NormalizeAndTypeCheck(ids, (int, long))
        keys = [datastore.Key.from_path(cls.kind(), id, parent=parent)
                for id in ids]
        if multiple:
            return get(keys, rpc=rpc)
        else:
            return get(keys[0], rpc=rpc)

    get_by_ids = get_by_id

    @classmethod
    def get_all(cls, order=None):
        query = cls.all()
        if order is not None:
            query = query.order(order)
        return query.fetch(None)

    @classmethod
    def check_exist(cls, **kwargs):
        query = cls.all(keys_only=True)
        for key, value in kwargs.iteritems():
            query = query.filter("%s =" % key, value)
        return query.count() > 0

    @classmethod
    def filter_one(cls, **filters):
        query = cls.all()
        for key, value in filters.iteritems():
            query = query.filter("%s =" % key, value)
        res = query.fetch(1)
        return res and res[0] or None


class StatsMixin(object):
    db_parent = BASEMODEL_PARENT

    @property
    def stats(self):
        dbstats = DBStats.get_by_id(self._stats_id)
        if not dbstats:
            dbstats = DBStats.filter_one(target_id=self.id, target_type=self.__class__.__name__)

            if not dbstats:
                dbstats = DBStats.create()
                dbstats.target_type = self.__class__.__name__
                dbstats.target_id = self.id

            if hasattr(self, "public"):
                dbstats.public = self.public
                
            dbstats.save()
            self._stats_id = str(dbstats.id)
            self.save()

        return dbstats


class DBStats(BaseModel):
    target_type = db.StringProperty()
    target_id = db.StringProperty()
    public = db.BooleanProperty(default=True)

    view_count = db.IntegerProperty(default=0)
    share_count = db.IntegerProperty(default=0)
    like_count = db.IntegerProperty(default=0)
    unlike_count = db.IntegerProperty(default=0)

    post_count = db.IntegerProperty(default=0)
    photo_count = db.IntegerProperty(default=0)
    comment_count = db.IntegerProperty(default=0)

    def increase(self, name, delta=1, commit=True):
            val = getattr(self, name)
            val += delta
            setattr(self, name, val)
            if commit:
                self.save()

    def decrease(self, name, delta=1, commit=True):
        val = getattr(self, name)
        val -= delta
        if val < 0:
            val = 0
        setattr(self, name, val)
        if commit:
            self.save()

    def set(self, name, value, commit=True):
        setattr(self, name, value)
        if commit:
            self.save()


# DataStore Models
class DBSiteSettings(BaseModel, StatsMixin):
    VERSION = 1.3  # update this if tables changed

    version = db.FloatProperty(default=0.0)
    title = db.StringProperty()
    subtitle = db.StringProperty()
    copyright = db.StringProperty(default="")
    theme = db.StringProperty(default="")
    ga_tracking_id = db.StringProperty()
    mirror_site = db.StringProperty(default="")    # mirror site for static files
    owner = db.StringProperty()
    inited = db.BooleanProperty(default=False)

    stats_id = db.StringProperty()

    @property
    def categories(self):
        return DBCategory.get_all(order="sort")

    @property
    def UserRoles(self):
        return DBUser.UserRoles

    @property
    def Templates(self):
        return DBCategory.Templates

    @property
    def Orders(self):
        return DBCategory.Orders

    @property
    def Themes(self):
        return common.BootsWatchThemes

    @property
    def MirrorSite(self):
        return self.mirror_site or ""

    @classmethod
    def get_site_settings(cls):
        return cls.get_by_key_name("DBSiteSettings/settings")

    @classmethod
    def create_settings(cls, **kwargs):
        return cls.get_or_insert("DBSiteSettings/settings", parent=BASEMODEL_PARENT, **kwargs)


class DBUser(BaseModel, StatsMixin):
    UserRoles = common.UserRoles

    protect_attrs = ["password", "email"]

    email = db.StringProperty(required=True)
    password = db.StringProperty()
    nickname = db.StringProperty(required=True)

    active = db.BooleanProperty(default=True)
    avatar = db.StringProperty(default="")
    role = db.StringProperty(choices=UserRoles, default=UserRoles[0])

    joined_date = db.DateTimeProperty(auto_now_add=True)

    _stats_id = db.StringProperty()

    @classmethod
    def create(cls, **kwargs):
        if "nickname" not in kwargs:
            kwargs["nickname"] = kwargs.get("email", "").split("@")[0]
        return BaseModel._create(cls, **kwargs)

    @property
    def avatar_url(self):
        if not self.avatar:
            return "http://www.gravatar.com/avatar/%s?s=64" % (
                hashlib.md5(self.email.lower().strip()).hexdigest())
        return self.avatar

    @classmethod
    def get_user_by_email(cls, email):
        return cls.filter_one(email=email.strip().lower())

    def to_dict(self):
        res = BaseModel.to_dict(self)
        res["avatar_url"] = self.avatar_url
        return res


class DBCategory(BaseModel, StatsMixin):
    Templates = common.Templates
    Orders = common.Orders

    url = db.StringProperty(default="")
    name = db.StringProperty(required=True)
    sort = db.IntegerProperty(default=0)
    posts_per_page = db.IntegerProperty(default=10)

    order = db.StringProperty(choices=Orders, default=Orders[1])
    template = db.StringProperty(choices=Templates, default=Templates[0])
    content = db.TextProperty(default="")  # for template "Text" only
    hidden = db.BooleanProperty(default=False)

    _stats_id = db.StringProperty()

    @property
    def Posts(self):
        return DBPost.all().filter("category_id =", self.id)

    def get_posts(self, page=1, per_page=10, include_no_published=False, start_cursor=""):
        if self.url == "":  # Home category
            query = DBPost.all()
        else:
            query = self.Posts

        query = query.order("-sticky").order(gae_order("post_date "+self.order))

        if not include_no_published:
            query = query.filter("public =", True)

        query.with_cursor(start_cursor=start_cursor)
        res = query.fetch(per_page)
        end_cursor = query.cursor()
        return res, end_cursor
        # return (items, cursor)

    @classmethod
    def get_by_url(cls, category_url):
        category_url = category_url.strip().lower()
        return cls.filter_one(url=category_url)


class DBPost(BaseModel, StatsMixin):
    additional_attrs = ["tags"]

    title = db.StringProperty(default="")
    body = db.TextProperty(default="")

    public = db.BooleanProperty(default=True)
    sticky = db.BooleanProperty(default=False)

    post_date = db.DateTimeProperty(auto_now_add=True)
    updated_date = db.DateTimeProperty(auto_now=True)

    category_id = db.StringProperty()
    author_id = db.StringProperty()

    _stats_id = db.StringProperty()
    _tag_list = db.ListProperty(str, default=[])

    @classmethod
    def create(cls, author_id, category_id, **kwargs):
        author_id = str(author_id)
        category_id = str(category_id)
        return BaseModel._create(cls, author_id=author_id, category_id=category_id, **kwargs)

    @property
    def author(self):
        return DBUser.get_by_id(self.author_id)

    @property
    def category(self):
        return self.category_id and DBCategory.get_by_id(self.category_id)

    @property
    def photos(self):
        return DBPhoto.all().filter("post_id =", self.id)

    @property
    def Comments(self):
        return DBComment.all().filter("post_id =", self.id)

    @property
    def tags(self):
        return self._tag_list

    @tags.setter
    def tags(self, value):
        self._tag_list = list(set(value))

    def to_dict(self):
        res = BaseModel.to_dict(self)
        author = self.author
        res["author"] = author.to_dict() if author else {}
        category = self.category
        res["category"] = category.to_dict() if category else {}
        res["photos"] = [photo.to_dict() for photo in self.photos if photo]
        res["tags"] = self.tags
        return res

    @classmethod
    def hot_posts(cls, count=8, order="view_count desc"):
        query = DBStats.all().filter("public =", True).filter("target_type =", cls.__name__).order(gae_order(order))
        ids = [stats.target_id for stats in query.fetch(count)]
        return [post for post in cls.get_by_ids(ids) if post and post.public]

    @classmethod
    def latest_posts(cls, count=8, order="updated_date desc"):
        return cls.all().filter("public =", True).order(gae_order(order)).fetch(count)


class DBTag(BaseModel, StatsMixin):
    created_date = db.DateTimeProperty(auto_now_add=True)
    _norm_name = db.StringProperty()
    name = db.StringProperty()
    post_count = db.IntegerProperty(default=0)
    _post_id_list = db.ListProperty(str, default=[])

    _stats_id = db.StringProperty()

    @property
    def post_ids(self):
        return self._post_id_list

    @post_ids.setter
    def post_ids(self, value):
        value = map(str, value)
        self._post_id_list = value

    def add_post_id(self, post_id):
        post_id = str(post_id)
        if post_id not in self._post_id_list:
            self.post_count += 1
            self._post_id_list.append(post_id)
            self.save()

    def remove_post_id(self, post_id):
        post_id = str(post_id)
        if post_id in self._post_id_list:
            self.post_count -= 1
            self._post_id_list.remove(post_id)
            self.save()

    def get_posts(self, page=1, per_page=10):
        posts_list = map(long, self._post_id_list)
        posts_list = posts_list[::-1]
        ids = posts_list[(page-1)*per_page:page*per_page]
        return [post for post in DBPost.get_by_ids(ids) if post and post.public]

    @classmethod
    def hot_tags(cls, count=16):
        return DBTag.all().order("-post_count").filter("post_count >", 0).fetch(count)

    @classmethod
    def get_tag_by_name(cls, name):
        return DBTag.filter_one(_norm_name=name.strip().lower())

    @classmethod
    def create(cls, name):
        return BaseModel._create(cls, name=name.strip(), _norm_name=name.strip().lower())


class DBPhoto(BaseModel, StatsMixin):
    created_date = db.DateTimeProperty(auto_now_add=True)
    url = db.TextProperty()
    url_thumb = db.TextProperty()
    mime = db.StringProperty()
    alt = db.StringProperty(default="")
    real_file = db.TextProperty()
    real_file_thumb = db.TextProperty()

    public = db.BooleanProperty(default=True)

    post_id = db.StringProperty()
    _stats_id = db.StringProperty()

    @property
    def post(self):
        return DBPost.get_by_id(self.post_id)

    @classmethod
    def hot_photos(cls, count=12, order="like_count desc"):
        query = DBStats.all().filter("public =", True).filter("target_type =", cls.__name__).order(gae_order(order))
        ids = [stats.target_id for stats in query.fetch(count)]
        return [photo for photo in cls.get_by_ids(ids) if photo and photo.public]


class DBComment(BaseModel, StatsMixin):
    created_date = db.DateTimeProperty(auto_now_add=True)
    author = db.StringProperty()
    content = db.TextProperty()
    deleted = db.BooleanProperty(default=False)

    parent_id = db.StringProperty(default="")
    post_id = db.StringProperty()
    _stats_id = db.StringProperty()

    @classmethod
    def create(cls, author, content, post_id, parent_id="", **kwargs):
        return BaseModel._create(cls,
            author=author, content=content,
            post_id=post_id, parent_id=parent_id,
            **kwargs)

    @property
    def post(self):
        return DBPost.get_by_id(self.post_id)

    def to_dict(self):
        res = BaseModel.to_dict(self)
        if self.deleted:
            from settings import gettext
            res["content"] = gettext("Comment Deleted")
        return res


def main():
    pass

if __name__ == '__main__':
    main()
