# -*- coding: utf-8 -*-
import hmac
import json
import os
import random
import time
from base64 import urlsafe_b64encode
from hashlib import sha1

import requests

DEFAULT_QINIU_UPLOAD_URL = 'http://up-z2.qiniu.com/'


def b(data):
    if isinstance(data, str):
        return data.encode('utf-8')
    return data


def s(data):
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    return data


def urlsafe_base64_encode(data):
    data = b(data)

    return s(urlsafe_b64encode(data))


class Qiniu(object):
    """七牛客户端
    """

    def __init__(self,
                 access_key,
                 secret_key,
                 bucket_name=None,
                 domain=None,
                 token_expires=3600,
                 time_delta=30,
                 qiniu_url=DEFAULT_QINIU_UPLOAD_URL):
        """初始化Qiniu类
        access_key 从七牛网站获得
        secret_key 从七牛网站获得
        bucket_name 要上传的空间 可在需要时调用 set_bucket_name 传入
        domain 空间绑定的域名，如果为空只返回文件的key，否则 'domain/key'
        """
        if not all([access_key, secret_key]):
            raise ValueError('invalid key')

        self.__access_key = access_key
        self.__secret_key = b(secret_key)
        self.__bucket_name = bucket_name
        self.__token = None
        self.__token_deadline = None
        self.time_delta = time_delta
        self.qiniu_url = qiniu_url
        self.token_expires = token_expires
        self.domain = domain

    def get_access_key(self):
        return self.__access_key

    def get_bucket_name(self):
        return self.__bucket_name

    def set_bucket_name(self, bucket_name):
        self.__bucket_name = bucket_name

    def __encode_token(self, data):
        data = b(data)
        hashed = hmac.new(self.__secret_key, data, sha1)
        return urlsafe_base64_encode(hashed.digest())

    def get_token(self):
        if not self.__bucket_name:
            raise ValueError('invalid bucket name')

        now = int(time.time())
        if self.__token and now < self.__token_deadline - self.time_delta:
            return self.__token

        scope = self.__bucket_name
        deadline = now + self.token_expires

        args = {'scope': scope, 'deadline': deadline}
        data = json.dumps(args, separators=(',', ':'))
        data = urlsafe_base64_encode(data)
        token = '{}:{}:{}'.format(self.__access_key,
                                  self.__encode_token(data), data)
        self.__token = token
        self.__token_deadline = deadline
        return self.__token

    def upload_file(self, file):
        """上传文件
        file 文件本地地址或者 file
        """
        if isinstance(file, str):
            resource = self.upload_localfile(file)

        elif isinstance(file, bytes):
            file = file.decode('utf-8')
            resource = self.upload_localfile(file)

        return resource

    def generate_key(self):
        return '{}{}'.format(int(time.time()), int(random.random() * 100))

    def generate_resource_path(self, key):
        res = key
        if self.domain:
            res = os.path.join(self.domain, key)

        return res

    def upload_localfile(self, file_path):
        """上传本地文件
        """
        payload = {'key': self.generate_key(), 'token': self.get_token()}

        with open(file_path, 'rb') as file:
            files = {'file': file}
            r = requests.post(self.qiniu_url, data=payload, files=files)
            r.raise_for_status

        return self.generate_resource_path(r.json().get('key'))
