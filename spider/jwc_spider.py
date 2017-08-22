# coding:utf-8
import random
import time
import os

from PIL import Image

from utils import *
from data_type import *
from spider.base_spider import WebdirverSpider
from config import LocalConfig

cf = LocalConfig()

PIC_DIR = cf.get_value("CAPTCHA", "JWC_PATH")


class JWCSpider(WebdirverSpider):
    """
    教务处爬虫
    """
    def __init__(self):
        super(JWCSpider, self).__init__()
        self._index_url = "http://jxgl.cuit.edu.cn/JXGL/xs/MainMenu.asp"
        self._login_url = "http://210.41.224.117/Login/xLogin/Login.asp"
        self._query_url = "http://jxgl.cuit.edu.cn/JXGL/Pub/InputXh.asp"
        self.code_file = ''
        self.__query_txt = cf.get_value("JWC_SPIDER", "QUERY_TXT") + '%'
        self.total_page = int(cf.get_value("JWC_SPIDER", "QUERY_PAGE"))

    @handle_exception()
    def login(self, username, password):
        """
        登录
        :param username:
        :param password:
        :return:
        """
        self.driver = self.get_driver()
        self.driver.delete_all_cookies()
        self.driver.get(self._index_url)
        self.driver.implicitly_wait(2)
        # self.driver.get(self._login_url)
        self.driver.execute_script('''document.getElementById("txtId").value = "%s";''' % username)
        self.driver.execute_script('''document.getElementById("txtMM").value = "%s";''' % password)
        check_code = self.__get_check_code()
        self.driver.execute_script('''document.getElementById("txtVC").value = "%s";''' % check_code)
        self.driver.execute_script('''document.getElementById("IbtnEnter").click();''')
        self.driver.implicitly_wait(2)
        alert = self.driver.switch_to_alert()
        try:
            if alert is not None:
                log(alert.text)
                return False
        except:
            self.driver.get_screenshot_as_file("login.png")
            if is_match(self.driver.page_source, "验证码不匹配"):
                log("验证码不匹配", err_code=LOGIN_CODE_ERROR)
                return False
            log("登录成功")
            self.driver.get(self._query_url)
            if is_match(self.driver.page_source, "按学号查找学生"):
                return True

    @handle_exception()
    def __get_check_code(self):
        """
        获取验证码
        :return:
        """
        self.code_file = os.path.join(PIC_DIR, self._get_file_name(time_flag=True))
        self.driver.get_screenshot_as_file(self.code_file)
        location = self.driver.find_element_by_id('verifypic').location
        size = self.driver.find_element_by_id('verifypic').size
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        a = Image.open(self.code_file)
        im = a.crop((left, top, right, bottom))
        im.save(self.code_file)
        time.sleep(1)
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
        re_data = []
        while curr_page <= self.total_page:
            if curr_page == 1:
                self.driver.execute_script('''document.getElementsByName("Bmdm")[0].value = "%s";''' % self.__query_txt)
                self.driver.execute_script('''document.getElementsByName("B1")[0].click();''')
            res_page = self.driver.page_source
            if is_match(res_page, "所属系科"):
                log("查询学号信息成功 -->page:%d" % curr_page)
            else:
                log("查询学生学号信息失败-->page:%d" % curr_page, err_code=GET_JWC_PAGE_ERROR)
                return
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
                    info["name"] = trim_all(xpath_match(row, './/td[7]/font/font/text()'))
                    info["sex"] = trim_all(xpath_match(row, './/td[8]/font/text()'))
                    info["in_school"] = trim_all(xpath_match(row, './/td[9]/font/text()'))
                    log("学号信息-->%s：%s" % (info["id"], str(info)))
                    re_data.append(info)
                try:
                    self.driver.find_element_by_xpath('//a[text()="后页"]').click()
                    curr_page += 1
                    self.driver.implicitly_wait(2)
                except:
                    log("所有信息获取完成")
                    break
            else:
                log("无任何学号信息", err_code=GET_JWC_NO_INFO_ERROR)
                return
        try:
            self.driver.quit()
        except:
            pass
        return re_data
