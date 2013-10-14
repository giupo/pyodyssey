# -*- coding:utf-8 -*-

from mock import patch, MagicMock, PropertyMock, Mock
from pyodyssey import OdysseyClient, AuthenticationException
import requests
import time

class MockResponse(object):
    def __init__(self, text = None, history=None, cookies=None):
        self.history = history
        self.text = text
        self.cookies = cookies

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, txt):
        self._text = txt


    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        self._cookies = value


def suc_res(*args, **kwargs):
    good_html = """<html><body>
    <form>
    <input type="hidden" name="xsauth" value="qazwsx123"/>
    </form>
    </body></html>"""

    cookiesHistory = dict(DSID='abcdefg123')
    cookies = dict(DSLastAccess=int(time.time()))
    history = [ MockResponse(cookies=cookiesHistory) ]
    return MockResponse(text=good_html, cookies=cookies, history=history)

def fail_res(*args, **kwargs):
    bad_html = """<html><body>
    <form>
    </form>
    </body>
    </html>"""
    cookiesHistory = dict(BOH='I dunno what to do with myself')
    cookies = dict(DSLastAccess=int(time.time()))
    history = [ MockResponse(cookies=cookies) ]
    return MockResponse(text=bad_html, cookies = cookies, history=history)


def test_connection_error():
    try:
        o = OdysseyClient('ovviamente.non.esisto.org', 'john', 'doe')
        o.auth()
        assert False
    except requests.ConnectionError:
        pass

def test_authentication_successful():
    with patch.object(requests.sessions.Session, 'request', return_value=suc_res()) as mock_method:
        o = OdysseyClient('localhost', 'john', 'doe')
        o.auth()

    print o.DSID
    print o.xsauth
    assert o.DSID == 'abcdefg123'
    assert o.xsauth == 'qazwsx123'



def test_authentication_has_to_fail():
    with patch.object(requests.sessions.Session, 'request', return_value=fail_res()) as mock_method:
        o = OdysseyClient('localhost', 'john', 'this is plainwrong')
        try:
            o.auth()
            assert False
        except AuthenticationException as e:
            pass
