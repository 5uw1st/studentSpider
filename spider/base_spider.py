# coding:utf-8
import os
import time
import hashlib

from requests.utils import dict_from_cookiejar
from selenium import webdriver

from db_manager import MongoDB
from captcha.jwc_captcha import JWCCaptcha
from captcha.xgw_captcha import XGWCaptcha
from data_type import SITE_TYPE_JWC, SITE_TYPE_XGW, CAPTCHA_NUMBER, \
    DRIVER_TYPE_CHROME, DRIVER_TYPE_FIREFOX, DRIVER_TYPE_PHANTOMJS
from config import local_config

chromeDriver = "driver/chromedriver"
os.environ["webdriver.chrome.driver"] = chromeDriver
phantomjsDriver = "driver/phantomjs"
os.environ["webdriver.phantomjs.driver"] = phantomjsDriver

db_name = local_config.get_value("DB_MONGODB", "DB_NAME")
table_name = local_config.get_value("DB_MONGODB", "CAPTCHA_TABLE")


class BaseSpider(object):
    """
    爬虫基类
    """
    def __init__(self):
        self.__username = None
        self.__password = None
        self._cookies = {}
        self.mongodb = MongoDB(db_name, table_name)
        self._input_flag = False

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

    def identify_captcha(self, pic_name, site_type=SITE_TYPE_XGW):
        """
        识别验证码
        :param pic_name:
        :param site_type:
        :return:
        """
        try:
            if site_type == SITE_TYPE_JWC:
                cap = JWCCaptcha(pic_name)
            elif site_type == SITE_TYPE_XGW:
                cap = XGWCaptcha(pic_name)
            else:
                cap = JWCCaptcha(pic_name)
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
            time_str = str(time.time()).encode("utf-8")
            m.update(time_str)
        else:
            m.update(content)
        file_name = "%s.png" % (str(m.hexdigest()))
        return file_name

    def _save_captcha_identify_log(self, file_name, code, status_code, site_type=SITE_TYPE_XGW, code_type=CAPTCHA_NUMBER):
        """
        保存验证码识别记录
        :param file_name:
        :param code:
        :param status_code:
        :param site_type:
        :param code_type:
        :return:
        """
        try:
            info = {
                "pic_name": file_name,
                "code": code,
                "status_code": status_code,
                "site_type": site_type,
                "code_type": code_type
            }
            if self.mongodb.insertOne(info):
                return True
            return False
        except Exception as e:
            return False

    def _save_file(self, file_name, content, is_pic=False):
        """
        保存文件内容(HTML)
        :param file_name:
        :param content:
        :param is_pic:
        :return:
        """
        try:
            if os.path.exists(file_name):
                return True
            mode = "w"
            if is_pic:
                mode = "wb"
            with open(file_name, mode) as f:
                f.write(content)
            return True
        except Exception as e:
            return False


class WebdirverSpider(BaseSpider):
    """
    浏览器模拟爬虫基类
    """
    def __init__(self):
        super(WebdirverSpider, self).__init__()
        self.driver = None

    def get_driver(self, browser_type=DRIVER_TYPE_CHROME):
        """
        获取浏览器对象
        :param browser_type:
        :return:
        """
        if browser_type == DRIVER_TYPE_CHROME:
            if os.name == "nt":
                return webdriver.Chrome(chromeDriver)
            else:
                return webdriver.Chrome()
        elif browser_type == DRIVER_TYPE_FIREFOX:
            pass
        elif browser_type == DRIVER_TYPE_PHANTOMJS:
            return webdriver.PhantomJS(phantomjsDriver)
        else:
            pass