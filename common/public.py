# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 15:18
# @Author  : 哎哟卧槽
# @Site    : 公共方法
# @File    : public.py
# @Software: PyCharm
import sys
import random, string
import requests
from requests.exceptions import ConnectTimeout


def random_string(num: int) -> str:
    """获取指定长度的随机字符串
    :param num: 随机字符串的长度
    :return:
    """
    str_ing = ''.join(random.sample(string.ascii_letters + string.digits, num - 1)).casefold()
    return 'a' + str_ing  # 保证是以字母开头


def get_response(url:str)->str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        else:
            print("状态为{};请检查网站是否正常工作".format(response.status_code))
            sys.exit(0)
    except ConnectTimeout as e:
        print("网站链接超时：{}".format(e.args))