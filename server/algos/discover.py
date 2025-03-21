from datetime import datetime
from typing import Optional

from server import config
from server.logger import logger
from server.utils import get_or_add_user

#import sqlalchemy
#from sqlalchemy import and_
from server.models import Post, UserFollows
import sqlalchemy as sa
from sqlalchemy import and_, or_
from server import db

uri = config.DISCOVER_FEED_URI
CURSOR_EOF = 'eof'



def handler(cursor: Optional[str], limit: int, requester_did: str) -> dict:

    #return {
    #    'cursor': CURSOR_EOF,
    #    'feed': []
    #}

    #stmt = sqlalchemy.select(Post).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)
    #posts = session.scalars(stmt).all()

    '''
    stmt = sqlalchemy.select(Follows).filter(Follows.did == requester_did)
    rows = session.execute(stmt).fetchone()

    if not rows:
        add_user(requester_did)
    '''

    #all_followed_dids = get_follows(requester_did)
    #logger.info(f"Retrieved {len(all_followed_dids)} for user {requester_did}")

    #stmt = sqlalchemy.select(Post).where(Post.discoverable and Post.reply_root is None and Post.reply_parent is None and not Post.did.in_(all_followed_dids)).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)
    #stmt = sqlalchemy.select(Post).filter(Post.discoverable).where(Post.did.not_in(all_followed_dids)).order_by(Post.indexed_at.desc()).limit(limit)
    #posts = session.scalars(stmt).all()

    user = get_or_add_user(requester_did)
    userfollows_dids = [uf.follows_did for uf in user.userfollows]

    '''
    stmt = sqlalchemy.select(UserFollows).filter(UserFollows.user_id == user.id)
    userfollows_dids = [uf.follows_did for uf in session.scalars(stmt).all()]

    if user.replies_off:
        where_stmt = and_(
            Post.discoverable == 1,
            Post.did.not_in(userfollows_dids),
            Post.reply_parent == None,
            Post.reply_root == None,
        )
    else:
        where_stmt = and_(
            Post.discoverable == 1,
            Post.did.not_in(userfollows_dids),
        )

    stmt = sqlalchemy.select(Post).where(where_stmt).order_by(Post.indexed_at.desc()).limit(limit)
    posts = session.scalars(stmt).all()
    '''

    if user.replies_off:
        where_stmt = and_(
            Post.discoverable == 1,
            Post.did.not_in(userfollows_dids),
            Post.reply_parent == None,
            Post.reply_root == None,
        )
    else:
        where_stmt = and_(
            Post.discoverable == 1,
            Post.did.not_in(userfollows_dids),
        )


    '''
    if user.replies_off:
        where_stmt = (
            (Post.discoverable == 1) &
            (Post.did.not_in(userfollows_dids)) &
            (Post.reply_parent == None) &
            (Post.reply_root == None)
        )
    else:
        where_stmt = (
            (Post.discoverable == 1) &
            (Post.did.not_in(userfollows_dids))
        )
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

    #posts = Post.select().where(where_stmt).order_by(Post.cid.desc()).order_by(Post.indexed_at.desc()).limit(limit)

    posts = db.session.scalars( sa.select(Post).where(where_stmt).order_by(Post.indexed_at.desc()).order_by(Post.cid.desc()).limit(limit) ).all()


    feed = [{'post': post.uri} for post in posts]

    cursor = CURSOR_EOF
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
