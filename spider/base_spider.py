# coding:utf-8


class BaseSpider(object):
    """
    爬虫基类
    """
    def __init__(self):
        self.__username = None
        self.__password = None
        self.__cookies = {}

    def login(self, username, password):
        """
        登录方法，需要重写
        :param username:
        :param password:
        :return:
        """
        pass

    def __get_check_code(self, page):
        """
        获取验证码方法，可重写
        :param page:
        :return:
        """
        pass

    def handle_cookies(self, cookies):
        """
        处理cookies
        :param cookies:
        :return:
        """
        pass