#from server.database import session, FeedUser, UserFollows, Post
#from server.client import bsky_client
import peewee
import requests
import time

from server import db
from server.models import FeedUser, UserFollows, UserList
from server.logger import logger


def get_or_add_user(requester_did):
    feed_user = db.session.scalar(sa.select(FeedUser).where(FeedUser.did == requester_did))

    if user:
        return feed_user
    else:
        try:
            with db.session.begin():
                feed_user = FeedUser(did=requester_did)
                db.session.add(feed_user)
                db.session.commit()

                more_follows = True
                cursor = ''

                while more_follows:
                    follows_batch = requests.get(
                        "https://bsky.social/xrpc/com.atproto.repo.listRecords",
                        params={
                            "repo": requester_did,
                            "collection": "app.bsky.graph.follow",
                            "cursor": cursor,
                            "limit": 100,
                        },
                    ).json()


                    follows = [{'feeduser_id': feed_user.id,'follows_did': elem['value']['subject'], 'uri': elem['uri']} for elem in follows_batch['records']]

                    if follows:
                        sa.insert(UserFollows).values(follows)
                        db.session.commit()

                    if 'cursor' in follows_batch:
                        cursor = follows_batch['cursor']
                    else:
                        more_follows = False
        except Exception as e:
            logger.info(e)
            db.session.rollback()
            feed_user = db.session.scalar(sa.select(FeedUser).where(FeedUser.did == requester_did))

    return feed_user
                