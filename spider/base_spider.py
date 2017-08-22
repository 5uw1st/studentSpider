# coding:utf-8
import os
import time
import hashlib

from requests.utils import dict_from_cookiejar
from selenium import webdriver

from captcha.jwc_captcha import JWCCaptcha
from captcha.xgw_captcha import XGWCaptcha

chromeDriver = "driver/chromedriver"
os.environ["webdriver.chrome.driver"] = chromeDriver
phantomjsDriver = "driver/phantomjs"
os.environ["webdriver.phantomjs.driver"] = phantomjsDriver


class BaseSpider(object):
    """
    爬虫基类
    """
    def __init__(self):
        self.__username = None
        self.__password = None
        self._cookies = {}

    def login(self, username, password):
        """
        登录方法，需要重写
        :param username:
        :param password:
        :return:
        """
        pass

    def __get_check_code(self, *args, **kwargs):
        """
        获取验证码方法，可重写
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def handle_cookies(self, cookies):
        """
        处理cookies
        :param cookies:
        :return:
        """
        try:
            res = dict_from_cookiejar(cookies)
        except Exception as e:
            res = {}
        return res

    def identify_captcha(self, pic_name, site_type=2):
        """
        识别验证码
        :param pic_name:
        :param site_type:
        :return:
        """
        try:
            if site_type == 1:
                cap = JWCCaptcha(pic_name)
            else:
                cap = XGWCaptcha(pic_name)
            code = cap.get_verify()
            if code.find("FAIL") >= 0:
                return False
            else:
                return code
        except Exception as e:
            return None

    def _get_file_name(self, content=None, time_flag=False):
        """
        通过MD5生成文件名
        :param content:
        :param time_flag:
        :return:
        """
        m = hashlib.md5()
        if time_flag:
            time_str = str(time.time())
            m.update(time_str)
        else:
            m.update(content)
        file_name = "%s.jpg" % (str(m.hexdigest()))
        return file_name


class WebdirverSpider(BaseSpider):
    """
    浏览器模拟爬虫基类
    """
    def __init__(self):
        super(WebdirverSpider, self).__init__()
        self.driver = None

    def get_driver(self, browser_type="Chrome"):
        """
        获取浏览器对象
        :param browser_type:
        :return:
        """
        if browser_type == "Chrome":
            return webdriver.Chrome(chromeDriver)
        else:
            return webdriver.PhantomJS(phantomjsDriver)
