import os
import logging

from dotenv import load_dotenv

from server.logger import logger

load_dotenv()

SERVICE_DID = os.environ.get('SERVICE_DID')
HOSTNAME = os.environ.get('HOSTNAME')
FLASK_RUN_FROM_CLI = os.environ.get('FLASK_RUN_FROM_CLI')
#MYSQL_CONN_STRING = os.environ.get('MYSQL_CONN_STRING')
HANDLE = os.environ.get('HANDLE')
PASSWORD = os.environ.get('PASSWORD')

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

if FLASK_RUN_FROM_CLI:
    logger.setLevel(logging.DEBUG)

if not HOSTNAME:
    raise RuntimeError('You should set "HOSTNAME" environment variable first.')

#if not MYSQL_CONN_STRING:
#    raise RuntimeError('You should set "MYSQL_CONN_STRING" environment variable first.')

if not (DB_NAME and DB_USER and DB_PASSWORD and DB_HOST and DB_PORT):
    raise RuntimeError('You should set all database environment variables first.')

if not HANDLE:
    raise RuntimeError('You should set "HANDLE" environment variable first.')

if not PASSWORD:
    raise RuntimeError('You should set "PASSWORD" environment variable first.')


if not SERVICE_DID:
    SERVICE_DID = f'did:web:{HOSTNAME}'

'''
FEED_URI = os.environ.get('FEED_URI')
if not FEED_URI:
    raise RuntimeError('Publish your feed first (run publish_feed.py) to obtain Feed URI. '
                       'Set this URI to "FEED_URI" environment variable.')
'''

FOLLOWING_FEED_URI = os.environ.get('FOLLOWING_FEED_URI')
DISCOVER_FEED_URI = os.environ.get('DISCOVER_FEED_URI')
LINKS_FEED_URI = os.environ.get('LINKS_FEED_URI')
SECRET_FEED_URI = os.environ.get('SECRET_FEED_URI')
MUTUALAID_FEED_URI = os.environ.get('MUTUALAID_FEED_URI')
UNITEDKINGDOM_FEED_URI = os.environ.get('UNITEDKINGDOM_FEED_URI')

def _get_bool_env_var(value: str) -> bool:
    if value is None:
        return False

    normalized_value = value.strip().lower()
    if normalized_value in {'1', 'true', 't', 'yes', 'y'}:
        return True

    return False


IGNORE_ARCHIVED_POSTS = _get_bool_env_var(os.environ.get('IGNORE_ARCHIVED_POSTS'))
IGNORE_REPLY_POSTS = _get_bool_env_var(os.environ.get('IGNORE_REPLY_POSTS'))
