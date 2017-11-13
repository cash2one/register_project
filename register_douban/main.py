#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: main.py
@time: 2017/11/13 21:37
"""
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

from common.ym51 import YM51
from common.verify import Yundama
from common.public import random_string
from common.content import RedisContent
from common.ymexception import GetMsnTimeOut

from config import *


class RegisterDouban(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
        self.driver = webdriver.Chrome("C:\chromedriver.exe", chrome_options=options)
        self.driver.get("https://accounts.douban.com/register?redir=https://m.douban.com")
        self.wait = WebDriverWait(self.driver, 20)
        self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY, YUNDAMA_API_URL)
        self.ym51 = YM51(YIMA_USERNAME, YIMA_PASSWORD)
        self.project = YIMA_ITEMID
        self.content = RedisContent(REDIS_HOST, REDIS_PORT)

    def register(self):
        mobile = self.ym51.get_mobile(self.project)
        input_mobile = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//input[@name='alias']")))
        input_mobile.clear()
        input_mobile.send_keys(mobile)
        password = random_string(10)
        input_password = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//input[@name='pass']")))
        input_password.clear()
        input_password.send_keys(password)
        name = random_string(7)
        input_name = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//input[@name='name']")))
        input_name.clear()
        input_name.send_keys(name)
        next_click = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//button[text()='下一步']")))
        sleep(1)
        next_click.click()
        sleep(2)
        code_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//a[text()='获取验证码']")))
        code_btn.click()
        yzm = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".code-pic>img")))
        url = yzm.get_attribute('src')
        cookies = self.driver.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.get('name')] = cookie.get('value')
        response = requests.get(url, cookies=cookies_dict)
        result = self.ydm.identify(stream=response.content)
        if not result:
            print('验证码识别失败, 跳过识别')
            return
        input_code = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//input[@placeholder='输入上图的单词']")))
        input_code.send_keys(result)
        sleep(2)
        try:
            msn = self.ym51.get_message(self.project, mobile)
            msn = re.search("\d+", msn).group()
            if msn:
                input_msn = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//input[@placeholder='验证码']")))
                input_msn.send_keys(msn)
                sleep(1)
            btn_end = self.wait.until(EC.presence_of_element_located((By.XPATH, "./*//button[text()='完成']")))
            btn_end.click()
            print(mobile, password)
            self.wait.until(EC.alert_is_present(), "注册成功，欢迎加入豆瓣, 要去登录吗？")
            alert = self.driver.switch_to_alert()
            alert.accept()
            self.content.insert("douban", mobile, password)
            self.driver.delete_all_cookies()
            self.driver.close()
        except GetMsnTimeOut as e:
            print("没有信息重新开启注册")
            self.driver.delete_all_cookies()
            self.driver.close()


if __name__ == '__main__':
    douban = RegisterDouban()
    num = 50
    while num >= 0:
        douban.register()
        num -= num



