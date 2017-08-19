# coding:utf-8
import random
import time

from utils import *
from data_type import *
from spider.base_spider import BaseSpider
from config import LocalConfig

cf = LocalConfig()


class JWCSpider(BaseSpider):
    """
    教务处爬虫
    """
    def __init__(self):
        super(JWCSpider, self).__init__()
        self._index_url = "http://xsc.cuit.edu.cn/SystemForm/main.htm"
        self._login_url = "http://210.41.224.117/Login/xLogin/Login.asp"
        self._query_url = "http://jxgl.cuit.edu.cn/JXGL/Pub/ShowXsXx.asp?Lm=%sBmDm=%s&Xq=s&Sw=%s&Dr=%s&Pg=%d"
        self.code_file = 'jwc_code.png'
        self.__query_txt = url_encode(cf.get_value("JWC_SPIDER", "QUERY_TXT"))
        self.total_page = int(cf.get_value("JWC_SPIDER", "QUERY_PAGE"))

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
            log("打开登录页面失败:%s" % self.__username, err_code=LOGIN_PAGE_ERROR)
            return False
        # 获取验证码
        code_key = xpath_match(page, '//input[@name="codeKey"]/@value')
        check_code = self.__get_check_code(code_key)
        if not check_code:
            log("验证码输入错误", err_code=LOGIN_CODE_INPUT_ERROR)
            return False

        # 准备post表单数据
        post_data = {
            "WinW": "1366",
            "WinH": "738",
            "txtId": self.__username,
            "txtMM": self.__password,
            "verifycode": check_code,
            "codeKey": code_key,
            "Login": "Check",
            "IbtnEnter.x": random.randint(20, 40),
            "IbtnEnter.y": random.randint(20, 40)
        }
        page_info = download(self._login_url, data=post_data, get_cookies=True)
        if not page_info:
            log("登录失败,返回信息失败", err_code=LOGIN_PAGE_ERROR)
            return False
        login_page, cookies = page_info
        if is_match(login_page, "用户名和密码均区分大小写"):
            log("用户名或密码错误", err_code=LOGIN_PASSWORD_ERROR)
            return False
        elif is_match(login_page, "验证码不匹配"):
            log("验证码不匹配", err_code=LOGIN_CODE_ERROR)
            return False
        elif is_match(login_page, "LoginOK"):
            log("登录成功", err_code=LOGIN_SUCC)
            self.__cookies = cookies
            return True
        else:
            log("登录失败，未知错误", err_code=LOGIN_UNKNOWN_ERROR)
            return False

    @handle_exception()
    def __get_check_code(self, key):
        """
        获取验证码
        :param key:
        :return:
        """
        code_url = "http://210.41.224.117/Login/xLogin/yzmDvCode.asp?k=%s&t=%s" % (key, int((time.time()*1000)))
        referer = self._login_url
        code_body = download(code_url, is_img=True, referer=referer)
        if not code_body:
            return
        with open(self.code_file, 'wb') as f:
            f.write(code_body)
        code = input("-->请输入验证码:")
        log("验证码:%s" % code)
        return code

    @handle_exception()
    def get_student_info(self):
        """
        获取学号等信息
        :return:
        """
        curr_page = 1
        base_url = self._query_url % (quote("限学号"), self.__query_txt, quote("校区"), quote("系科"), quote("升"))
        re_data = []
        while curr_page <= self.total_page:
            query_url = base_url % curr_page
            res_page = download(query_url, cookies=self.__cookies)
            if not res_page:
                log("查询学生学号信息失败-->page:%d" % curr_page, err_code=GET_JWC_PAGE_ERROR)
            student_num = reg_match(res_page, r">学号＝.+?</b>\]的学生一共有 <b>(\d+)<")
            if curr_page == 1:
                log("学号为[%s]的学生人数总共为:%s" % (self.__query_txt, student_num))
            elements = xpath_match(res_page, '//table[@cols="12"]/tbody[2]/tr', get_one=False)
            if elements and len(elements) > 0:
                log("本页共有学生学号信息数:%d -->page:%d" % (len(elements), curr_page))
                for row in elements:
                    info = {}
                    info["location"] = trim_all(xpath_match(row, './/td[2]/font/text()'))
                    info["institute"] = trim_all(xpath_match(row, './/td[3]/font/text()'))
                    info["major"] = trim_all(xpath_match(row, './/td[4]/font/text()'))
                    info["class"] = trim_all(xpath_match(row, './/td[5]/font/text()'))
                    info["id"] = trim_all(xpath_match(row, './/td[6]/font/text()'))
                    info["name"] = trim_all(xpath_match(row, './/td[7]/font/text()'))
                    info["sex"] = trim_all(xpath_match(row, './/td[8]/font/text()'))
                    info["in_school"] = trim_all(xpath_match(row, './/td[9]/font/text()'))
                    log("学号信息-->%s：%s" % (info["id"], str(info)))
                    re_data.append(info)
                curr_page += 1
            else:
                log("无任何学号信息", err_code=GET_JWC_NO_INFO_ERROR)
                return
