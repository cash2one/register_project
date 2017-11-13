#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: content.py
@time: 2017/11/13 23:04
"""
import redis


class RedisContent(object):

    def __init__(self, host, port):
        self.content = redis.StrictRedis(host, port)

    def insert(self, name, mobile, password):
        self.content.set("{}:{}".format(name, mobile), password)
if __name__ == '__main__':
    pass