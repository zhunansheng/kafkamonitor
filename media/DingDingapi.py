# -*- coding: utf-8 -*-
import datetime
import json
import time
import urllib2
import urllib
import urllib2
import sys
import re
import base64
from urlparse import urlparse
import cookielib

def send_mess(mess,chat_cmdb_url):

    chat_textmod = {
    "msgtype": "markdown",
    "markdown": {
        "title": "sql审计平台",
        "text": mess
    }
}
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/json"}
    chat_textmod = json.dumps(chat_textmod)
    req = urllib2.Request(url=chat_cmdb_url, data=chat_textmod, headers=header_dict)
    res = urllib2.urlopen(req)
    res = res.read()
