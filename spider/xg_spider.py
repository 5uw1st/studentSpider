# coding:utf-8
import time

from studentSpider.utils import *
from studentSpider.data_type import *


class XGSpider(object):
    def __init__(self):
        self.__username = None
        self.__password = None
        self.__cookies = {}
        self._index_url = "http://xsc.cuit.edu.cn/SystemForm/main.htm"
        self._login_url = "http://xsc.cuit.edu.cn/UserLogin.html"
        self.code_file = 'code.png'

    @handle_exception()
    def login(self, username, password):
        """
        登录
        :return:
        """
        log("开始登录中...")
        self.__username = username
        self.__password = password
        page = download(self._login_url)
        if not page:
            log("打开登录页面失败:%s" % self.username, err_code=LOGIN_PAGE_ERROR)
            return False
        # 准备post表单数据
        view_state = xpath_match(page, '//input[@id="__VIEWSTATE"]/@value')
        view_state_tor = xpath_match(page, '//input[@id="__VIEWSTATEGENERATOR"]/@value')
        eventval = xpath_match(page, '//input[@id="__EVENTVALIDATION"]/@value')
        # 获取验证码
        check_code = self.__get_check_code(page)
        if not check_code:
            log("验证码输入错误", err_code=LOGIN_CODE_INPUT_ERROR)
        post_data = {
            "__VIEWSTATE": view_state,
            "__VIEWSTATEGENERATOR": view_state_tor,
            "__EVENTVALIDATION": eventval,
            "UserName": self.__username,
            "UserPass": self.__password,
            "CheckCode": check_code,
            "Btn_OK.x": "51",
            "Btn_OK.y": "37"
        }
        page_info = download(self._login_url, data=post_data, get_cookies=True)
        if not page_info:
            log("登录失败,返回信息失败", err_code=LOGIN_PAGE_ERROR)
            return False
        login_page, cookies = page_info

        if is_match(login_page, "用户名或密码错误"):
            log("用户名或密码错误", err_code=LOGIN_PASSWORD_ERROR)
            return False
        elif is_match(login_page, "验证码已经过期"):
            log("验证码已经过期", err_code=LOGIN_CODE_ERROR)
            return False
        elif is_match(login_page, r"location\.href='SystemForm/main\.htm'"):
            log("登录成功", err_code=LOGIN_SUCC)
            self.__cookies = cookies
            return True
        else:
            log("登录失败,未知错误", err_code=LOGIN_UNKNOWN_ERROR)
            return False

    @handle_exception()
    def __get_check_code(self, page):
        """
        获取验证码
        :param page:
        :return:
        """
        code_url = "http://xsc.cuit.edu.cn/" + xpath_match(page, '//img[@border="0"]/@src') \
                   or "http://xsc.cuit.edu.cn/default3.html"
        code_body = download(code_url, is_img=True)
        if not code_body:
            return
        with open(self.code_file, 'wb') as f:
            f.write(code_body)
        code = input("-->请输入验证码:")
        log("验证码:%s" % code)
        return code
