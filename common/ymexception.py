#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: ymexception.py
@time: 2017/11/13 22:54
"""


class MobileError(Exception):
    """号码错误"""


class GetMsnTimeOut(Exception):
    """获取信息超时"""

