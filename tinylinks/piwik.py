from hashlib import md5
from time import time
from datetime import datetime, timedelta
import os


def __get_random_string(length=500):
    """
    Return a random string

    :param length: Length
    :type length: inte
    :rtype: str
    """
    return md5(os.urandom(length)).hexdigest()


def _get_random_visitor_id(id_length):
    """
    Return a random visitor ID

    :rtype: str
    """
    visitor_id = __get_random_string()
    return visitor_id[:id_length]


def parse_cookie(cookie):
    if cookie:
        cookie = cookie.split('.')
        return {'_id': cookie[0], '_idts': cookie[1], '_idvc': int(cookie[2]), 'unknown': cookie[3],
                '_viewts': cookie[4]}
    else:
        return {}


def _calculate_visit(viewts, now_ts):
    visit = datetime.fromtimestamp(float(viewts))
    now = datetime.fromtimestamp(float(now_ts))
    if (now - visit) > timedelta(minutes=30):
        return now_ts
    else:
        return viewts


def _compose_cookie(parsed):
    return '{_id}.{_idts}.{_idvc}.{unknown}.{_viewts}.'.format(**parsed)


def response_cookie(cookie):
    now = int(time())

    if cookie:
        parsed = parse_cookie(cookie)
    else:
        visitor_id = _get_random_visitor_id(16)
        parsed = {'_id': visitor_id, '_idts': now, '_idvc': 0, '_viewts': now, 'unknown': now}
        cookie = _compose_cookie(parsed)

    parsed['unknown'] = now
    parsed['_viewts'] = _calculate_visit(parsed['_viewts'], now)
    parsed['_idvc'] += 1
    return _compose_cookie(parsed), cookie
