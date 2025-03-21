from datetime import datetime
from flask_login import UserMixin
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from server import db

class FeedUser(db.Model):
    __tablename__ = 'feeduser'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    did: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, unique=True, nullable=False)
    replies_off: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)

    dbuser: so.Mapped["DbUser"] = so.relationship(back_populates="feeduser")
    subscribes_to: so.Mapped[List["UserList"]] = so.relationship(back_populates="feedusers")
    userfollows: so.Mapped[List["UserFollows"]] = so.relationship(back_populates="feedusers")
    subfeeds: so.Mapped[List["SubfeedMember"]] = so.relationship(back_populates="feeduser")


class DbUser(UserMixin, db.Model):
    __tablename__ = 'dbuser'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("feeduser.id"))
    password: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)

    feeduser: so.Mapped["FeedUser"] = so.relationship(back_populates="dbuser")

    def __repr__(self):
        return '<User {}>'.format(self.user_handle)

class UserList(db.Model):
    __tablename__ = 'userlist'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("feeduser.id"))
    subscribes_to_did: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    subscribes_to_handle: so.Mapped[str] = so.mapped_column(sa.String(255))
    subscribes_to_disp_name: so.Mapped[str] = so.mapped_column(sa.String(255))

    feedusers: so.Mapped[List["FeedUser"]] = so.relationship(back_populates="subscribes_to")



class UserFollows(db.Model):
    __tablename__ = 'userfollows'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("feeduser.id"))
    follows_did: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    follows_handle: so.Mapped[str] = so.mapped_column(sa.String(255))
    follows_disp_name: so.Mapped[str] = so.mapped_column(sa.String(255))

    feedusers: so.Mapped[List["FeedUser"]] = so.relationship(back_populates="userfollows")

class Subfeed(db.Model):
    __tablename__ = 'subfeed'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feed_name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False, unique=True)

    members: so.Mapped[List["SubfeedMember"]] = so.relationship(back_populates="subfeed")

class SubfeedMember(db.Model):
    __tablename__ = 'subfeedmember'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    subfeed_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("subfeed.id"))
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("feeduser.id"))

    subfeed: so.Mapped["Subfeed"] = so.relationship(back_populates="members")
    feeduser: so.Mapped["FeedUser"] = so.relationship(back_populates="subfeeds")
    
class Post(db.Model):
    __tablename__ = 'post'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    uri: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, nullable=False)
    cid: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    did: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    reply_parent: so.Mapped[str] = so.mapped_column(sa.String(255))
    reply_root: so.Mapped[str] = so.mapped_column(sa.String(255))
    discoverable: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    has_link: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    link_only: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    userlist_only: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    subfeed_only: so.Mapped[int] = so.mapped_column(sa.Integer)
    indexed_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, nullable=False)
