# -*- coding:utf-8 -*-

# Copyright (c) <2013> <Giuseppe Acito>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import requests
import time
import re

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from urlparse import urlunparse

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# made just to easly switch from http to https

__PROTOCOL__ = 'https'
__WELCOME_PATH__ = "/dana-na/auth/url_default/welcome.cgi"
__LOGIN_PATH__ = "/dana-na/auth/url_default/login.cgi"
__STARTER_PATH__ = "/dana/home/starter0.cgi"
__INFRANET_PATH__ = "/dana/home/infranet.cgi"
REALM = 'LAPTOP_Compliance'


class AuthenticationException(Exception):
    pass


class OdysseyClient(object):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.interval = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:22.0) Gecko/20100101 Firefox/22.0",  # noqa
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa
            "Accept-Language": "it,en-us;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": self.host,
        }
        # questo l'ho preso dall'HTML, NON VOGLIO SAPERE NIENTE!!!...
        self.successful_res_junkie = \
            re.compile("\nnotification: (\d+)\ninterval: (\d+)\n")


    def _welcome(self):
        self.DSLastAccess = str(int(time.time()))
        cookies = dict(
            lastRealm=REALM,
            DSSIGNIN="url_default",
            DSPREAUTH="",
            path="/dana-na",
            expires="12-Nov-1996",  # Only god knows...
            DSLastAccess=self.DSLastAccess)

        url = urlunparse((__PROTOCOL__,
                          self.host,
                          __WELCOME_PATH__, None, None, None))
        log.debug(url)
        self.last_res = requests.get(
            url,
            cookies=cookies,
            headers=self.headers,
            verify=False)

    def _login(self):
        headers = dict(self.headers)
        headers.update({
            "Referer": urlunparse((
                __PROTOCOL__,
                self.host,
                __WELCOME_PATH__, None, None, None)),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": self.host})

        cookies = dict(
            lastRealm=REALM,
            DSSIGNIN="url_default",
            DSSignInURL="/",
            DSLastAccess=self.DSLastAccess)
        log.debug("Cookies: %s", str(cookies))

        url = urlunparse(
            (__PROTOCOL__,
             self.host,
             __LOGIN_PATH__, None, None, None))
        log.debug(url)

        post_data = dict(
            tz_offset="60",
            username=self.username,
            password=self.password,
            realm=REALM,
            btnSubmit="Sign In")
        log.debug("POST data: %s", str(post_data))

        self.last_res = requests.post(
            url,
            cookies=cookies,
            headers=headers,
            data=post_data,
            verify=False)
        # allow_redirects=False)

        # Don't ask, won't tell.
        log.debug(self.last_res.text)
        try:
            self.DSID = self.last_res.history[0].cookies['DSID']
            bs = BeautifulSoup(self.last_res.text, "lxml")
            xsauth = bs.find('input').get('value')
            self.xsauth = xsauth
            log.debug("DSID: %s" % self.DSID)
            log.debug("xsauth: %s" % self.xsauth)
        except KeyError as e:
            log.error(e)
            raise AuthenticationException()
        except AttributeError as e:
            # log.error(self.last_res.text)
            if self.last_res.text.find("Your password will expire in ") != -1:
                raise Exception(
                    "Your Passowrd will expire soon, update it and rerun")
            else:
                raise AuthenticationException()

    def _starter1(self):
        # to be honest, i ignore why I should make this GET request...
        headers = dict(self.headers)
        headers.update({
            "Referer":
            urlunparse((__PROTOCOL__,
                        self.host,
                        __STARTER_PATH__, None, None, None))})

        url = urlunparse((__PROTOCOL__,
                          self.host,
                          __STARTER_PATH__, None, None, None))
        log.debug(url)
        cookies = dict(
            DSSignInURL="/",
            DSLastAccess=self.DSLastAccess,
            DSID=self.DSID,
            DSFirstAccess=self.last_res.cookies['DSLastAccess'])

        params = dict(check="yes")

        res = requests.get(
            url,
            headers=headers,
            params=params,
            cookies=cookies,
            verify=False)
        log.debug(res.text)
        res.raise_for_status()

    def _starter2(self):
        headers = dict(self.headers)
        headers.update({
            "Referer": urlunparse((
                __PROTOCOL__,
                self.host,
                __STARTER_PATH__,
                None, None, None)),
            "Content-Type": "application/x-www-form-urlencoded",
        })

        url = urlunparse((__PROTOCOL__,
                          self.host,
                          __STARTER_PATH__, None, None, None))
        log.debug(url)
        post_data = dict(
            xsauth=self.xsauth,
            tz_offset="60",
            clienttime=str(int(time.time())),
            url="",
            activex_enabled="0",
            java_enabled="1",
            power_user="0",
            grab="1",
            browserproxy="",
            browsertype="",
            browserproxysettings="",
            check="yes",
            citrixinstalled="")

        cookies = dict(DSID=self.DSID)

        self.last_res = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=post_data,
            verify=False,
            allow_redirects=False)

    def heartbeat(self):
        log.info("sending heartbeat...")
        url = urlunparse((__PROTOCOL__,
                          self.host,
                          __INFRANET_PATH__, None, None, None))
        params = dict(
            heartbeat="1",
            clientlessEnabled="1",
            sessionExtension="0",
            notification_originalmsg="")

        cookies = dict(
            DSLastAccess=self.DSLastAccess,
            DSID=self.DSID
        )

        self.last_res = requests.post(
            url,
            headers=self.headers,
            cookies=cookies,
            data=params,
            verify=False,
            allow_redirects=True)

        self.DSLastAccess = str(int(time.time()))

        log.debug(self.last_res.text)
        result = self.successful_res_junkie.match(self.last_res.text)

        if result is not None:
            self.interval = int(result.group(2))
            log.info("heartbeat successful")
        else:
            log.info("Holy crap, looks like you're not authenticated...")
            self.auth()

        return True

    def auth(self):
        self._welcome()
        self._login()
        self._starter1()
        self._starter2()

    def run(self):
        self.auth()
        try:
            while(self.heartbeat()):  # the level of shame here is 9000
                time.sleep(self.interval / 10)
        except KeyboardInterrupt:
            pass


def main():
    parser = ArgumentParser(description="Client for Odyssey Networks")
    parser.add_argument("host", help="Host IP of Odyssey website")
    parser.add_argument("user", help="Username")
    parser.add_argument("password", help="Password")
    parser.add_argument("--debug", default=True)
    args = parser.parse_args()
    log.debug(args.host)
    odyssey = OdysseyClient(args.host, args.user, args.password)
    odyssey.run()


if __name__ == '__main__':
    main()
