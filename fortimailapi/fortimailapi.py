#!/usr/bin/env python
# Copyright 2017 Fortinet, Inc.
#
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

###################################################################
#
# fortimailapi.py aims at simplyfing the configuration and
# integration of FortiMail configuration using the restapi
#
###################################################################

import requests

import json

import logging

LOG = logging.getLogger('fortimailapi')


class FortiMailAPIError(Exception):
    """Base exception for FortiMail API errors."""


class FortiMailAuthError(FortiMailAPIError):
    """Raised when authentication/login fails."""

class FortiMailAPI(object):
    def __init__(self):
        self._https = False

        self._fortiversion = "Version is set when logged"

        self._session = requests.session()  # use single session

        self._session.verify = False

        self.flg_debug = False

        LOG.setLevel(logging.INFO)

    def logging(self, response):
        try:
            LOG.debug("Request : %s on url : %s  ", response.request.method,
                      response.request.url)
            LOG.debug("Response : http code %s  reason : %s  ",
                      response.status_code, response.reason)
            LOG.debug("raw response:  %s ", response.content)
        except:
            LOG.warning("method errors in request when global")

    def debug(self, status):
        if status == 'on':
            LOG.setLevel(logging.DEBUG)
            self.flg_debug = True
        else:
            LOG.setLevel(logging.INFO)
            self.flg_debug = False

    def format_response(self, res):
        try:
            return json.loads(res.content.decode('utf-8'))
        except Exception:
            return {
                'http_status': getattr(res, 'status_code', None),
                'raw': res.content.decode('utf-8', errors='replace')
            }


    def https(self, status):
        if status == 'on':
            self._https = True
        if status == 'off':
            self._https = False

    def store_session_cookie(self, cookieJar):
        LOG.debug(cookieJar)
        self._session.cookies=cookieJar

    def login(self, host, username, password):
        self.host = host
        if self._https is True:
            self.url_prefix = 'https://' + self.host
        else:
            self.url_prefix = 'http://' + self.host

        url = self.url_prefix + '/api/v1/AdminLogin'
        payload = '{"name":"' + username + '","password":"' + password + '"}'
        self._session.headers = {'content-type': "application/json" }
        try:
            res = self._session.post(url, data=payload)
        except requests.RequestException as exc:
            LOG.debug("request exception during login: %s", exc)
            raise FortiMailAPIError("Connection error during login") from exc

        # always log request/response debug info
        self.logging(res)

        # try to parse JSON body if present
        try:
            body = res.json()
        except Exception:
            body = None

        # if HTTP error code, raise
        if not res.ok:
            msg = None
            if isinstance(body, dict):
                msg = body.get('errorMsg') or body.get('message')
            raise FortiMailAPIError(
                "Login request failed: {}".format(msg or res.reason)
            )

        # some FortiMail responses use an "errorType"/"errorMsg" payload
        if isinstance(body, dict) and (body.get('errorType') or body.get('errorMsg')):
            err = body.get('errorMsg') or body.get('message') or str(body)
            raise FortiMailAuthError("Authentication failed: {}".format(err))

        # success
        if self.flg_debug:
            LOG.debug("result = %s", res)
        try:
            self._fortiversion = body.get('product_version', 'Unknown') if isinstance(body, dict) else 'Unknown'
        except Exception:
            self._fortiversion = 'Unknown'
        self.store_session_cookie(res.cookies)

    def get_version(self):
        return self._fortiversion

    def cmdb_url(self, resource, dom=None):

        url_postfix = '/api/v1/'
        if dom:
            url_postfix += "domain/"+dom+"/"
        url_postfix += resource
        return self.url_prefix+url_postfix

    def get(self, resource, domain=None):
        url = self.cmdb_url(resource, domain)
        res = self._session.get(url)
        LOG.debug("in GET function")
        return self.format_response(res)

    def post(self, resource, domain=None, data=None):
        url = self.cmdb_url(resource, domain)
        self._session.headers = {'content-type': "application/json"}
        res = self._session.post(url, data=data)
        LOG.debug("in POST function")
        return self.format_response(res)

    def put(self, resource, domain=None, data=None):
        url = self.cmdb_url(resource, domain)
        self._session.headers = {'content-type': "application/json"}
        formatted_json = data.decode('utf8').replace("'", '"')
        res = self._session.put(url, data=formatted_json)
        LOG.debug("in PUT function. Data: "+formatted_json)
        return self.format_response(res)

    def delete(self, resource, domain=None, data=None):
        url = self.cmdb_url(resource, domain)
        self._session.headers = {'content-type': "application/json"}
        res = self._session.delete(url, data=data)
        LOG.debug("in DELETE function")
        return self.format_response(res)

    def license(self):
        url = self.cmdb_url("SysStatusLicinfo/")
        res = self._session.get(url)
        return json.loads(res.content.decode('utf-8'))

