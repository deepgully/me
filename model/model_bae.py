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
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import object_session

db = SQLAlchemy(session_options={"expire_on_commit": False})

import hashlib
import common


def bind_app(app):
    db.app = app
    db.init_app(app)
    init_database(app)
    app.teardown_request(clean_cache)
    return app


def drop_all():
    db.drop_all()


def create_all():
    db.create_all()


def create_default_settings(app):
    title = app.config["SiteTitle"]

    settings = DBSiteSettings(title=title,
                              subtitle=app.config["SiteSubTitle"],
                              owner=app.config["OwnerEmail"],
                              version=DBSiteSettings.VERSION)
    settings.id = 1

    from apis import User, Post, Category
    home = Category.default_category()

    owner = User.get_user_by_email(app.config["OwnerEmail"])
    if not owner:
        owner = User.create_user(email=app.config["OwnerEmail"],
                                 password=app.config["DefaultPassword"],
                                 role="Owner")

    post = Post.get_by_id(1)
    if not post:
        Post.create_post(owner, home, title=common.Welcome_Title % title,
            body=common.Welcome_Post % title)

    settings.inited = True
    settings.save()
    return settings


def init_database(app):
    settings = None
    try:
        settings = DBSiteSettings.get_site_settings()

        if not settings or not settings.inited:
            raise Exception("Can not get site settings")

        if settings.version < DBSiteSettings.VERSION:
            raise Exception("Database expired")
    except:
        from alembic import command

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


__db_get_cache = {}


def clean_cache(*args, **kwargs):
    __db_get_cache.clear()


def _norm_key(cls, id):
    return "%s_%s" % (cls.__name__, id)


def _get(cls, ids):
    multiple = isinstance(ids, (list, tuple, set))
    if not multiple:
        ids = [ids]

    results = []
    for id in ids:
        if id is None:
            results.append(None)
            continue
        key = _norm_key(cls, id)

        if key not in __db_get_cache:
            db_object = cls.query.get(id)
            __db_get_cache[key] = db_object
        else:
            db_object = __db_get_cache[key]

        if (db_object is not None) and (db_object not in db.session):
            session = object_session(db_object)
            if session is not None:
                session.expunge(db_object)
            try:
                db.session.add(db_object)
            except:
                db_object = db.session.merge(db_object)
                __db_get_cache[key] = db_object

        results.append(db_object)

    if multiple:
        return results
    else:
        return results[0]


def _remove(cls, ids):
    multiple = isinstance(ids, (list, tuple, set))
    if not multiple:
        ids = [ids]

    keys = [_norm_key(cls, id) for id in ids]
    results = [__db_get_cache.pop(k, None) for k in keys]

    if multiple:
        return results
    else:
        return results[0]


def _update(cls, objs):
    multiple = isinstance(objs, (list, tuple, set))
    if not multiple:
        objs = [objs]

    keys = []
    for obj in objs:
        if hasattr(obj, "id"):
            key = _norm_key(cls, obj.id)
            __db_get_cache[key] = obj
            keys.append(key)
        else:
            keys.append(None)

    if multiple:
        return keys
    else:
        return keys[0]


class ModelMixin(object):
    protect_attrs = []

    @classmethod
    def get_by_id(cls, id):
        return _get(cls, id)

    @classmethod
    def get_by_ids(cls, ids):
        return _get(cls, ids)

    @classmethod
    def get_all(cls, order=None):
        query = cls.query
        if order is not None:
            query = query.order_by(order)
        return query.all()

    @classmethod
    def check_exist(cls, **kwargs):
        return cls.query.filter_by(**kwargs).count() > 0

    @classmethod
    def filter_one(cls, **filters):
        return cls.query.filter_by(**filters).first()

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return obj

    def to_dict(self):
        _res = {}
        if hasattr(self, "stats"):
            _res["stats"] = self.stats.to_dict()
        res = dict([(k, getattr(self, k)) for k in self.__dict__.keys() if
                     (not k.startswith("_") and k not in self.protect_attrs)])
        res.update(_res)
        return res

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            self.commit()

        _update(self.__class__, self)

    def delete(self, commit=True):
        if hasattr(self, "stats"):
            dbstats = DBStats.get_by_id(self._stats_id)
            _remove(DBStats, self._stats_id)
            if dbstats:
                db.session.delete(dbstats)

        _remove(self.__class__, self.id)
        db.session.delete(self)
        if commit:
            self.commit()
        return self

    def commit(self):
        ModelMixin.commit()

    def update(self, commit=True, **kwargs):
        need_save = False
        for attr, val in kwargs.iteritems():
            if getattr(self, attr, None) != val:
                if (not attr.startswith("_")) and (attr != "id") and (attr in self.__dict__):
                    need_save = True
                    setattr(self, attr, val)
                    if attr == "public" and hasattr(self, "stats"):
                        self.stats.public = val
                        self.stats.save()

        if need_save:
            self.save(commit)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


class StatsMixin(object):
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
            self._stats_id = dbstats.id
            self.save()

        return dbstats


class DBStats(db.Model, ModelMixin):
    __tablename__ = "db_stats"

    id = db.Column(db.Integer, primary_key=True)

    target_type = db.Column(db.String(128))
    target_id = db.Column(db.Integer)
    public = db.Column(db.Boolean, default=True)

    view_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)

    post_count = db.Column(db.Integer, default=0)
    photo_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

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


########################################
## Data Models
########################################
class DBSiteSettings(db.Model, ModelMixin):
    VERSION = 1.3  # update this if tables changed

    id = db.Column(db.Integer, primary_key=True)

    version = db.Column(db.Float, default=0.0)
    title = db.Column(db.String(512))
    subtitle = db.Column(db.String(128))
    copyright = db.Column(db.String(512), default="")
    theme = db.Column(db.String(128), default="")
    ga_tracking_id = db.Column(db.String(128))
    mirror_site = db.Column(db.String(512), default="")    # mirror site for static files
    owner = db.Column(db.String(256))
    inited = db.Column(db.Boolean, default=False)

    def __init__(self, title, subtitle, owner, version):
        self.title = title
        self.subtitle = subtitle
        self.owner = owner
        self.version = version

    @property
    def categories(self):
        return DBCategory.get_all(order=DBCategory.sort)

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
        return cls.get_by_id(1)


class DBUser(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_user"

    UserRoles = common.UserRoles

    id = db.Column(db.Integer, primary_key=True)

    protect_attrs = ["password", "posts",  "email"]

    email = db.Column(db.String(128), unique=True, index=True)
    password = db.Column(db.String(256))
    nickname = db.Column(db.String(40), unique=True, index=True)
    active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(512), default="")
    role = db.Column(db.Enum(*UserRoles), default="User")
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))

    def __init__(self, email,
                 nickname="", avatar="", role="User", active=True):
        self.email = email
        self.nickname = nickname or self.email.split("@")[0]
        self.avatar = avatar
        self.role = role
        self.active = active

    def __repr__(self):
        return '<DBUser %r : %s>' % (self.nickname, self.email)

    @property
    def avatar_url(self):
        if not self.avatar:
            return "http://www.gravatar.com/avatar/%s?s=64" % (
                hashlib.md5(self.email.lower().strip()).hexdigest())
        return self.avatar

    @classmethod
    def get_user_by_email(cls, email):
        return cls.filter_one(email=email)

    def to_dict(self):
        res = ModelMixin.to_dict(self)
        res["avatar_url"] = self.avatar_url
        return res


class DBCategory(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_category"

    Templates = common.Templates
    Orders = common.Orders

    protect_attrs = ["posts"]

    id = db.Column(db.Integer, primary_key=True)

    url = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    sort = db.Column(db.Integer, default=0)
    posts_per_page = db.Column(db.Integer, default=5)

    order = db.Column(db.Enum(*Orders), default=Orders[1])
    template = db.Column(db.Enum(*Templates), default=Templates[0])
    content = db.Column(db.Text)  # for template "Text" only
    hidden = db.Column(db.Boolean, default=False)

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))

    def __init__(self, url, name, sort=0, order=Orders[1], template=Templates[0]):
        self.url = url
        self.name = name
        self.sort = sort
        self.order = order
        self.template = template

    def __repr__(self):
        return '<DBCategory %r : %s>' % (self.url, self.name)

    @property
    def Posts(self):
        return self.posts

    def get_posts(self, page=1, per_page=10, include_no_published=False, start_cursor=""):
        if self.url == "":  # Home category
            query = DBPost.query
        else:
            query = self.Posts

        query = query.order_by("sticky desc").order_by("post_date " + self.order)

        if not include_no_published:
            query = query.filter_by(public=True)

        # return (items, cursor) for GAE compatibility
        return query.paginate(page, per_page, False).items, ""

    @classmethod
    def get_by_url(cls, category_url):
        return cls.filter_one(url=category_url)


class DBPost(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_post"

    protect_attrs = ["_author", "author", "_category", "category", "photos", "comments",
                     "Comments", "stats", "tags", "_tag_list"]

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(128))
    body = db.Column(db.Text)

    public = db.Column(db.Boolean, default=True)
    sticky = db.Column(db.Boolean, default=False)

    post_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # post event datetime
    updated_date = db.Column(db.DateTime, onupdate=datetime.utcnow, index=True)  # updated datetime

    category_id = db.Column(db.Integer, db.ForeignKey(DBCategory.__tablename__ + '.id', ondelete="SET NULL"), index=True)
    _category = db.relationship('DBCategory', backref=db.backref('posts', lazy='dynamic'))

    author_id = db.Column(db.Integer, db.ForeignKey(DBUser.__tablename__ + ".id", ondelete="SET NULL"), index=True)
    _author = db.relationship('DBUser', backref=db.backref('posts', lazy='dynamic'))

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))
    _tag_list = db.Column(db.Text, default="")


    def __init__(self, author_id, category_id, title="", body="", post_date=None):
        self.title = title
        self.body = body
        self.author_id = author_id
        self.category_id = category_id
        if post_date is None:
            post_date = datetime.utcnow()
        self.post_date = post_date
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return '<Post %s>' % self.id

    @property
    def author(self):
        return DBUser.get_by_id(self.author_id)

    @property
    def category(self):
        return self.category_id and DBCategory.get_by_id(self.category_id)

    @property
    def Comments(self):
        return self.comments.order_by("created_date").all()

    @property
    def tags(self):
        if not self._tag_list:
            return []
        return [tag for tag in self._tag_list.split(",") if tag and tag.strip()]

    @tags.setter
    def tags(self, value):
        self._tag_list = ",".join(list(set(value)))

    def to_dict(self):
        res = ModelMixin.to_dict(self)
        res["author"] = self.author.to_dict() if self.author else {}
        category = self.category
        res["category"] = category.to_dict() if category else {}
        res["photos"] = [photo.to_dict() for photo in self.photos if photo]
        res["tags"] = self.tags
        return res

    @classmethod
    def hot_posts(cls, count=8, order="view_count desc"):
        query = DBStats.query.filter_by(public=True).filter_by(target_type=cls.__name__).order_by(order)
        ids = [stats.target_id for stats in query.limit(count).all()]
        return [post for post in cls.get_by_ids(ids) if post and post.public]

    @classmethod
    def latest_posts(cls, count=8, order="updated_date desc"):
        return cls.query.filter_by(public=True).order_by(order).limit(count).all()


class DBTag(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_tag"

    protect_attrs = ["_norm_name"]

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    _norm_name = db.Column(db.String(64))

    name = db.Column(db.String(64))

    post_count = db.Column(db.Integer, default=0)

    _post_id_list = db.Column(db.Text, default="")

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))

    def __init__(self, name):
        self.name = name.strip()
        self._norm_name = name.strip().lower()
        self.post_count = 0
        self._post_id_list = ""

    @property
    def post_ids(self):
        if not self._post_id_list:
            return []
        return [str(id) for id in self._post_id_list.split(",") if id and id.strip()]

    @post_ids.setter
    def post_ids(self, value):
        value = map(str, value)
        self._post_id_list = ",".join(value)

    def add_post_id(self, post_id):
        post_id = str(post_id)
        if post_id not in self.post_ids:
            self.post_count += 1
            self._post_id_list += "," + str(post_id)
            self.save()

    def remove_post_id(self, post_id):
        post_id = str(post_id)
        post_ids = self.post_ids
        if post_id in post_ids:
            post_ids.remove(post_id)
            self.post_count -= 1
            self.post_ids = post_ids
            self.save()

    def get_posts(self, page=1, per_page=10):
        posts_list = map(long, self.post_ids)
        posts_list = posts_list[::-1]
        ids = posts_list[(page-1)*per_page:page*per_page]
        return [post for post in DBPost.get_by_ids(ids) if post and post.public]

    @classmethod
    def hot_tags(cls, count=16):
        query = DBTag.query.order_by("post_count desc").filter(DBTag.post_count > 0)
        return query.limit(count).all()

    @classmethod
    def get_tag_by_name(cls, name):
        return DBTag.filter_one(_norm_name=name.strip().lower())


class DBPhoto(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_photo"

    protect_attrs = ["post", "_post"]

    id = db.Column(db.Integer, primary_key=True)

    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(1024),  default="")
    url_thumb = db.Column(db.String(1024), default="")
    mime = db.Column(db.String(128), default="application/octet-stream")
    alt = db.Column(db.String(140), default="")
    real_file = db.Column(db.String(1024), default="")
    real_file_thumb = db.Column(db.String(1024), default="")

    public = db.Column(db.Boolean, default=True)

    post_id = db.Column(db.Integer, db.ForeignKey(DBPost.__tablename__ + ".id", ondelete="SET NULL"), index=True)
    _post = db.relationship('DBPost', backref=db.backref('photos', lazy='dynamic'))

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))

    def __init__(self, url="", real_file="", alt="", mime="application/octet-stream"):
        self.url = url
        self.alt = alt
        self.mime = mime
        self.real_file = real_file

    @property
    def post(self):
        return DBPost.get_by_id(self.post_id)

    @classmethod
    def hot_photos(cls, count=12, order="like_count desc"):
        query = DBStats.query.filter_by(public=True).filter_by(target_type=cls.__name__).order_by(order)
        ids = [stats.target_id for stats in query.limit(count).all()]
        return [photo for photo in cls.get_by_ids(ids) if photo]


class DBComment(db.Model, ModelMixin, StatsMixin):
    __tablename__ = "db_comment"

    protect_attrs = ["post", "_post"]

    id = db.Column(db.Integer, primary_key=True)

    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, default="")
    deleted = db.Column(db.Boolean, default=False)

    parent_id = db.Column(db.Integer, default=-1)
    post_id = db.Column(db.Integer, db.ForeignKey(DBPost.__tablename__ + ".id", ondelete="SET NULL"), index=True)
    _post = db.relationship('DBPost', backref=db.backref('comments', lazy='dynamic'))

    _stats_id = db.Column(db.Integer, db.ForeignKey(DBStats.__tablename__ + '.id', ondelete="SET NULL"))

    def __init__(self, author, content, post_id, parent_id=-1):
        self.author = author
        self.content = content
        self.post_id = post_id
        self.parent_id = parent_id

    @property
    def post(self):
        return DBPost.get_by_id(self.post_id)

    def to_dict(self):
        res = ModelMixin.to_dict(self)
        if self.deleted:
            from settings import gettext
            res["content"] = gettext("Comment Deleted")
        return res

