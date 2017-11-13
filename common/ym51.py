# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 15:39
# @Author  : 哎哟卧槽
# @Site    : 获取手机号以及验证码接口
# @File    : ym51.py
# @Software: PyCharm
import sys
import json
import time
from urllib.parse import urlencode, quote
from json.decoder import JSONDecodeError
from common.ymexception import GetMsnTimeOut, MobileError

from common.public import get_response

base_url = "http://api.51ym.me/UserInterface.aspx?"
# 登录接口
login_url = base_url + "action=login&username={user}&password={password}"
# 获取用户信息接口
get_account_info_url = base_url + "action=getaccountinfo&token={token}&format=1"
# 获取手机号
get_mobile_url = base_url + "action=getmobile&itemid={projectid}&token={token}"
# 释放手机号
freed_mobile_url = base_url + "action=release&mobile={mobile}&itemid={projectid}&token={token}"
# 释放全部手机号
freed_mobile_all_url = base_url + "action=releaseall&token={token}"
# 加入黑名单
add_ignore_url = base_url + "action=addignore&mobile={mobile}&itemid={projectid}&token={token}"
# 获取短信
get_message_url = base_url + "action=getsms&mobile={mobile}&itemid={projectid}&token={token}"
# 发送短信
send_sms_url = base_url + "action=sendsms&mobile={mobile}&itemid={projectid}&sms={message}&token={token}"
# 获取发送短信状态
send_message_status_url = base_url + "action=getsendsmsstate&mobile={mobile}&itemid={projectid}&token={token}"

error_code = {
        "1001": "参数token不能为空",
        "1002": "参数action不能为空",
        "1003": "参数action错误",
        "1004": "token失效",
        "1005": "用户名或密码错误",
        "1006": "用户名不能为空",
        "1007": "密码不能为空",
        "1008": "账户余额不足",
        "1009": "账户被禁用",
        "1010": "参数错误",
        "1011": "账户待审核",
        "1012": "登录数达到上限",
        "2001": "参数itemid不能为空",
        "2002": "项目不存在",
        "2003": "项目未启用",
        "2004": "暂时没有可用的号码",
        "2005": "获取号码数量已达到上限",
        "2006": "参数mobile不能为空",
        "2007": "号码已被释放",
        "2008": "号码已离线",
        "2009": "发送内容不能为空",
        "2010": "号码正在使用中",
        "3001": "尚未收到短信",
        "3002": "等待发送",
        "3003": "正在发送",
        "3004": "发送失败",
        "3005": "订单不存在",
        "3006": "专属通道不存在",
        "3007": "专属通道未启用",
        "3008": "专属通道密码与项目不匹配",
        "9001": "系统错误",
        "9002": "系统异常",
        "9003": "系统繁忙"
}


class YM51(object):

    def __init__(self, username:str, password:str):
        """登录获取token
        :param username: 用户名
        :param password: 密码
        """
        response = get_response(login_url.format(user=username, password=password))
        result = response.split('|')
        if result[0] == "success":
            self.token = result[1]

    def check_account(self)->bool:
        """检查用户是否可用
        :return: true or false
        """
        response = get_response(get_account_info_url.format(token=self.token))
        result = response.split("|")
        if result[0] == "success":
            info = json.loads(result[1])
            if info.get("Status") == 1:
                print("账户正常:{}".format(result))
                return True
            raise error_code.get(response)

    def get_mobile(self, project_id: str, **kwargs: dict)->str:
        """获取手机号
        :param project_id: 项目id
        :param kwargs: 额外参数
        :return:
        """
        response = get_response(get_mobile_url.format(projectid=project_id, token=self.token))
        result = response.split("|")
        if result[0] == "success":
            return result[1]
        elif response == "2004":  # 防止暂时没有可用号码
            print(error_code.get(response))
            self.get_mobile(project_id, **kwargs)
        else:
            raise MobileError

    def get_message(self, project_id: str, mobile: str, release: "str"=None)->str:
        """获取短信息
        :param project_id: 项目编号
        :param mobile:电话号码
        :param release: 是否释放该号码
        :return:
        """
        num = 12
        while num >= 0:
            if not release:
                response = get_response(get_message_url.format(mobile=mobile,
                                                               projectid=project_id,
                                                               token=self.token))
            else:
                response = get_response(get_message_url.format(mobile=mobile,
                                                               projectid=project_id,
                                                               token=self.token) + "&release=1")
            result = response.split("|")
            if result[0] == "success":
                print("验证码为：{}".format(result[1]))
                return result[1]
            time.sleep(5)
            print("还在获取短信验证码倒数第{}次".format(num))
            num -= 1
        else:
            print("获取信息超时")
            raise GetMsnTimeOut

    def releaseall(self)->bool:
        """释放所有号码
        :return:
        """
        response = get_response(freed_mobile_all_url.format(token=self.token))
        if response == "success":
            print("释放成功")
            return True
        raise error_code.get(response)

    def add_ignore(self, mobile: str, project_id: str)->bool:
        """拉黑电话号码
        :param mobile:手机号
        :param project_id: 项目编号
        :return:
        """
        response = get_response(add_ignore_url.format(mobile=mobile,
                                                      projectid=project_id,
                                                      token=self.token))
        if response == "success":
            print("拉黑成功")
            return True
        print("{}拉黑失败".format(mobile))
        raise error_code.get(response)

    def send_sms(self, mobile: str, project_id: str, sms: str)->bool:
        """发送信息
        :param mobile: 电话号码
        :param project_id:项目编号
        :param sms:发送消息内容
        :return:
        """
        sms = quote(sms)
        response = get_response(send_sms_url.format(mobile=mobile,
                                                    projectid=project_id,
                                                    message=sms,
                                                    token=self.token))
        if response == "success":
            print("消息发送成功；开始确认状态")
            return self.get_send_sms_state(mobile, project_id)
        raise error_code.get(response)

    def get_send_sms_state(self, mobile: str, project_id: str)->bool:
        """获取发送消息的状态
        :param mobile: 电话号码
        :param project_id: 项目编号
        :return:
        """
        num = 12
        while True:
            response = get_response(send_message_status_url.format(mobile=mobile,
                                                                   projectid=project_id,
                                                                   token=self.token))
            if response == "success":
                print("状态确认成功")
                return True
            elif response == "fail":
                print("短信发送不成功")
                return False
            elif error_code.get(response):
                raise error_code.get(response)
            else:
                num -= 1
                time.sleep(5)
        else:
            return False