# coding:utf-8
<<<<<<< HEAD
import os

from requests.utils import dict_from_cookiejar
from selenium import webdriver

chromeDriver = "driver/chromedriver"
os.environ["webdriver.chrome.driver"] = chromeDriver
phantomjsDriver = "driver/phantomjs"
os.environ["webdriver.phantomjs.driver"] = phantomjsDriver
=======
from requests.utils import dict_from_cookiejar
>>>>>>> 0c6cb4ed541727b7997974a3e5a88a4b11444900


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
<<<<<<< HEAD


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
=======
>>>>>>> 0c6cb4ed541727b7997974a3e5a88a4b11444900
