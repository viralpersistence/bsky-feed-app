from datetime import datetime
from typing import Optional

from server import config, db
from server.logger import logger
from server.utils import get_or_add_user

import sqlalchemy as sa
from sqlalchemy import or_, and_
from server.models import Post, Subfeed, SubfeedMember

uri = config.MUTUALAID_FEED_URI
CURSOR_EOF = 'eof'

feed_name = 'mutualaid'

def handler(cursor: Optional[str], limit: int, requester_did: str) -> dict:
    subfeed = db.session.scalar(sa.select(Subfeed).where(Subfeed.feed_name == feed_name))
    subfeed_id = subfeed.id

    user = get_or_add_user(requester_did)

    member_ids = [member.feeduser.did for member in subfeed.members]

    '''
    if user.replies_off:
        where_stmt = (
            (Post.userlist_only == 0) &
            (Post.link_only == 0) &
            (Post.did.in_(member_ids))
            (Post.subfeed_only.in_([None, subfeed_id])) &
            (Post.reply_parent == None) &
            (Post.reply_root == None)
        )

    else:
        where_stmt = (
            (Post.userlist_only == 0) &
            (Post.link_only == 0) &
            (Post.did.in_(member_ids)) &
            (Post.subfeed_only.in_([None, subfeed_id]))
        )
    '''

    if user.replies_off:
        where_stmt = and_(
            Post.userlist_only == 0,
            Post.link_only == 0,
            Post.did.in_(member_ids),
            Post.subfeed_only.in_([None, subfeed_id]),
            Post.reply_parent == None,
            Post.reply_root == None,
        )

    else:
        where_stmt = and_(
            Post.userlist_only == 0,
            Post.link_only == 0,
            Post.did.in_(member_ids),
            Post.subfeed_only.in_([None, subfeed_id]),
        )

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

    #posts = Post.select().where(where_stmt).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)
    posts = db.session.scalars( sa.select(Post).where(where_stmt).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)  ).all()

    feed = [{'post': post.uri} for post in posts]

    cursor = CURSOR_EOF
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
