# -*- coding: utf-8 -*-
"""
Cookie-related utilities.
"""
from __future__ import absolute_import
import time
import calendar

from six.moves.http_cookiejar import CookieJar, Cookie


def jar_to_har(cookiejar):
    """ Convert CookieJar to HAR cookies format """
    return [cookie_to_har(c) for c in cookiejar]


def har_to_jar(cookiejar, har_cookies):
    """ Add HAR cookies to the cookiejar """
    for c in har_cookies:
        cookiejar.set_cookie(har_to_cookie(c))


def har_to_cookie(har_cookie):
    """
    Convert a cookie dict in HAR format to a Cookie instance.

    >>> har_cookie =  {
    ...     "name": "TestCookie",
    ...     "value": "Cookie Value",
    ...     "path": "/foo",
    ...     "domain": "www.janodvarko.cz",
    ...     "expires": "2009-07-24T19:20:30Z",
    ...     "httpOnly": True,
    ...     "secure": True,
    ...     "comment": "this is a test"
    ... }
    >>> cookie = har_to_cookie(har_cookie)
    >>> cookie.name
    'TestCookie'
    >>> cookie.value
    'Cookie Value'
    >>> cookie.port
    >>> cookie.domain
    'www.janodvarko.cz'
    >>> cookie.path
    '/foo'
    >>> cookie.secure
    True
    >>> cookie.expires
    1248463230
    >>> cookie.comment
    'this is a test'
    >>> cookie.get_nonstandard_attr('HttpOnly')
    True


    >>> har_cookie =  {
    ...     "name": "TestCookie2",
    ...     "value": "Cookie Value",
    ...     "expires": 1248463230,
    ... }
    >>> cookie = har_to_cookie(har_cookie)
    >>> cookie.name
    'TestCookie2'
    >>> cookie.expires
    1248463230
    """

    expires_timestamp = None
    if har_cookie.get('expires'):
        expires = har_cookie['expires']
        if isinstance(expires, int):
            expires_timestamp = expires
        else:
            expires = time.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
            expires_timestamp = calendar.timegm(expires)

    kwargs = dict(
        version=har_cookie.get('version') or 0,
        name=har_cookie['name'],
        value=har_cookie['value'],
        port=None,
        domain=har_cookie.get('domain', ''),
        path=har_cookie.get('path', '/'),
        secure=har_cookie.get('secure', False),
        expires=expires_timestamp,
        discard=False,
        comment=har_cookie.get('comment'),
        comment_url=bool(har_cookie.get('comment')),
        rest={'HttpOnly': har_cookie.get('httpOnly')},
        rfc2109=False,
    )
    kwargs['port_specified'] = bool(kwargs['port'])
    kwargs['domain_specified'] = bool(kwargs['domain'])
    kwargs['domain_initial_dot'] = kwargs['domain'].startswith('.')
    kwargs['path_specified'] = bool(kwargs['path'])
    return Cookie(**kwargs)


def cookie_to_har(cookie):
    """
    Convert a Cookie instance to a dict in HAR cookie format.
    """
    c = {
        'name': cookie.name,
        'value': cookie.value,
        'secure': cookie.secure,
    }
    if cookie.path_specified:
        c['path'] = cookie.path

    if cookie.domain_specified:
        c['domain'] = cookie.domain

    if cookie.expires:
        tm = time.gmtime(cookie.expires)
        c['expires'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", tm)

    http_only = cookie.get_nonstandard_attr('HttpOnly')
    if http_only is not None:
        c['httpOnly'] = bool(http_only)

    if cookie.comment:
        c['comment'] = cookie.comment

    return c
