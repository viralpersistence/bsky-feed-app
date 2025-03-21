from datetime import datetime
from typing import Optional

from server import config
from server.logger import logger
import sqlalchemy as sa
from sqlalchemy import and_, or_
from server.models import Post, UserList#, User, Follows
from server import db
from server.utils import get_or_add_user

uri = config.SECRET_FEED_URI
CURSOR_EOF = 'eof'


def handler(cursor: Optional[str], limit: int, requester_did: str) -> dict:

    user = get_or_add_user(requester_did)

    if user.replies_off:
        where_stmt = and_(
            UserList.feeduser_id == user.id,
            Post.reply_parent == None,
            Post.reply_root == None,
        )
    else:
        where_stmt = UserList.feeduser_id == user.id

    '''
    if user.replies_off:
        where_stmt = (
            (UserList.feeduser_id == user.id) &
            (Post.reply_parent == None) &
            (Post.reply_root == None)
        )
    else:
        where_stmt = (UserList.feeduser_id == user.id)
    '''

    if cursor:
        if cursor == CURSOR_EOF:
            return {
                'cursor': CURSOR_EOF,
                'feed': []
            }
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        indexed_at, cid = cursor_parts
        indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)

        #where_stmt = (where_stmt & ( ( (Post.indexed_at == indexed_at) & (Post.cid < cid)  ) | (Post.indexed_at < indexed_at) ) )
        where_stmt = and_(where_stmt, or_( and_(Post.indexed_at == indexed_at, Post.cid < cid), Post.indexed_at < indexed_at  ))

    #posts = Post.select().join(UserList, on=(Post.did == UserList.subscribes_to_did)).where(where_stmt).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)
    posts = db.session.scalars( sa.select(Post).join(UserList, Post.did == UserList.subscribes_to_did).where(where_stmt).order_by(Post.indexed_at.desc()).order_by(Post.cid.desc()).limit(limit) ).all()


    '''
    if user.replies_off:
        where_stmt = and_(
            UserList.user_id == user.id,
            Post.reply_parent == None,
            Post.reply_root == None
        )
    else:
        where_stmt = UserList.user_id == user.id


    stmt = sqlalchemy.select(Post).join(UserList, Post.did == UserList.subscribes_to_did).where(where_stmt).order_by(Post.indexed_at.desc()).limit(limit)

    posts = session.scalars(stmt).all()


    if cursor:
        if cursor == CURSOR_EOF:
            return {
                'cursor': CURSOR_EOF,
                'feed': []
            }
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        indexed_at, cid = cursor_parts
        indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)
        #posts = posts.where(((Post.indexed_at == indexed_at) & (Post.cid < cid)) | (Post.indexed_at < indexed_at))
        posts = [post for post in posts if (post.indexed_at == indexed_at and post.cid < cid) or post.indexed_at < indexed_at]
    '''

    feed = [{'post': post.uri} for post in posts]

    cursor = CURSOR_EOF
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
