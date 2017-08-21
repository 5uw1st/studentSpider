# coding:utf-8
import time
import random

from utils import *
from data_type import *
from spider.base_spider import BaseSpider


class XGSpider(BaseSpider):
    """
    学工网爬虫
    """
    def __init__(self):
        super(XGSpider, self).__init__()
        self._index_url = "http://xsc.cuit.edu.cn/SystemForm/Class/MyStudent.aspx"
        self._login_url = "http://xsc.cuit.edu.cn/UserLogin.html"
        self.code_file = 'xg_code.png'

    @handle_exception()
    def login(self, username, password):
        """
        登录
        :return:
        """
        log("开始登录中...")
        self.__username = username
        self.__password = password
        page_info = download(self._login_url, get_cookies=True)
        if not page_info:
            log("打开登录页面失败:%s" % self.__username, err_code=LOGIN_PAGE_ERROR)
            return False
        page, cookies = page_info
        cookies = self.handle_cookies(cookies)
        # 准备post表单数据
        view_state = xpath_match(page, '//input[@id="__VIEWSTATE"]/@value')
        view_state_tor = xpath_match(page, '//input[@id="__VIEWSTATEGENERATOR"]/@value')
        eventval = xpath_match(page, '//input[@id="__EVENTVALIDATION"]/@value')
        # 获取验证码
        check_code = self.__get_check_code(page, cookies)
        if not check_code:
            log("验证码输入错误", err_code=LOGIN_CODE_INPUT_ERROR)
        post_data = {
            "__VIEWSTATE": view_state,
            "__VIEWSTATEGENERATOR": view_state_tor,
            "__EVENTVALIDATION": eventval,
            "UserName": self.__username,
            "UserPass": self.__password,
            "CheckCode": check_code,
            "Btn_OK.x": random.randint(20, 50),
            "Btn_OK.y": random.randint(20, 50)
        }
        page_info = download(self._login_url, data=post_data, get_cookies=True, cookies=cookies)
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
            self._cookies = self.handle_cookies(cookies)
            return True
        else:
            log("登录失败,未知错误", err_code=LOGIN_UNKNOWN_ERROR)
            return False

    @handle_exception()
    def __get_check_code(self, page, cookies):
        """
        获取验证码
        :param page:
        :param cookies:
        :return:
        """
        code_url = "http://xsc.cuit.edu.cn/" + xpath_match(page, '//img[@border="0"]/@src') \
                   or "http://xsc.cuit.edu.cn/default3.html"
        referer = self._login_url
        code_body = download(code_url, is_img=True, referer=referer, cookies=cookies)
        if not code_body:
            return
        with open(self.code_file, 'wb') as f:
            f.write(code_body)
        code = input("-->请输入验证码:")
        log("验证码:%s" % code)
        return code

    def get_user_info(self):
        """
        获取用户信息
        :return: 
        """
        info_page = download(self._index_url, cookies=self._cookies)
        if not info_page:
            log("打开学生信息页面失败")
            return
        student_id = xpath_match(info_page, '//input[@id="Student11_StudentNo"]/@value')
        student_name = xpath_match(info_page, '//input[@id="Student11_StudentName"]/@value')
        student_sex = xpath_match(info_page, '//input[@name="Student11$Sex"][@checked="checked"]/@value')
        birthday = xpath_match(info_page, '//input[@id="txtStudent11aBirthDay"]/@value')
        national = xpath_match(info_page, '//select[@id="Student11_National"]/option[@selected="selected"]/text()')
        polity = xpath_match(info_page, '//select[@id="Student11_Polity"]/option[@selected="selected"]/text()')
        native_place = xpath_match(info_page, '//input[@id="Student11_NativePlace"]/@value')
        in_time = xpath_match(info_page, '//input[@id="txtStudent11aInTime"]/@value')
        province = xpath_match(info_page, '//select[@id="province"]/option[@selected="selected"]/text()')
        city = xpath_match(info_page, '//select[@id="city"]/option[@selected="selected"]/text()')
        county = xpath_match(info_page, '//select[@id="county"]/option[@selected="selected"]/text()')
        id_card = xpath_match(info_page, '//input[@id="Student21_IdCard"]/@value')
        family_reg = xpath_match(info_page, '//input[@name="Student21$FamillyReg"][@checked="checked"]/@value')
        examinee_type = xpath_match(info_page, '//select[@id="Student21_ExamineeType"]/option[@selected="selected"]/@value')
        get_type = xpath_match(info_page, '//select[@id="Student21_GetType1"]/option[@selected="selected"]/text()')
        exam_no = xpath_match(info_page, '//input[@id="Student21_ExamineeNo"]/@value')
        bank_name = xpath_match(info_page, '//select[@id="Student21_BankName"]/option[@selected="selected"]/text()')
        bank_no = xpath_match(info_page, '//input[@id="Student21_BankNo"]/@value')
        father_name = xpath_match(info_page, '//input[@id="Student41_FatherName"]/@value')
        mather_name = xpath_match(info_page, '//input[@id="Student41_MotherName"]/@value')
        father_unit = xpath_match(info_page, '//input[@id="Student41_FatherUnit"]/@value')
        mather_unit = xpath_match(info_page, '//input[@id="Student41_MotherUnit"]/@value')
        father_tel = xpath_match(info_page, '//input[@id="Student41_FatherTel"]/@value')
        mather_tel = xpath_match(info_page, '//input[@id="Student41_MotherTel"]/@value')
        family_address = xpath_match(info_page, '//input[@id="Student41_FamilyAddress"]/@value')
        family_post = xpath_match(info_page, '//input[@id="Student41_FamillyPost"]/@value')
        family_tel = xpath_match(info_page, '//input[@id="Student41_FamillyTel"]/@value')
        spe_type = xpath_match(info_page, '//select[@id="Student51_SpeType"]/option[@selected="selected"]/text()')
        in_status = xpath_match(info_page, '//select[@id="Student51_InStatus"]/option[@selected="selected"]/text()')
        college_no = xpath_match(info_page, '//select[@id="Student51_CollegeNo"]/option[@selected="selected"]/text()')
        specialty_no = xpath_match(info_page, '//select[@id="Student51_SpecialtyNo"]/option[@selected="selected"]/text()')
        grade = xpath_match(info_page, '//select[@id="Student51_Grade"]/option[@selected="selected"]/text()')
        class_no = xpath_match(info_page, '//select[@id="Student51_ClassNo"]/option[@selected="selected"]/text()')
        dorm_address = xpath_match(info_page, '//input[@Wid="Student51_DormAddress"]/@value')
        user_info = {}
        user_info["student_id"] = student_id
        user_info["student_name"] = student_name
        user_info["student_sex"] = student_sex
        user_info["birthday"] = birthday
        user_info["national"] = national
        user_info["polity"] = polity
        user_info["native_place"] = native_place
        user_info["in_time"] = in_time
        user_info["province"] = province
        user_info["city"] = city
        user_info["county"] = county
        user_info["id_card"] = id_card
        user_info["family_reg"] = family_reg
        user_info["examinee_type"] = examinee_type
        user_info["get_type"] = get_type
        user_info["student_id"] = student_id
        user_info["exam_no"] = exam_no
        user_info["bank_name"] = bank_name
        user_info["bank_no"] = bank_no
        user_info["father_name"] = father_name
        user_info["mather_name"] = mather_name
        user_info["father_tel"] = father_tel
        user_info["mather_tel"] = mather_tel
        user_info["father_unit"] = father_unit
        user_info["mather_unit"] = mather_unit
        user_info["family_address"] = family_address
        user_info["family_post"] = family_post
        user_info["family_tel"] = family_tel
        user_info["spe_type"] = spe_type
        user_info["in_status"] = in_status
        user_info["college_no"] = college_no
        user_info["specialty_no"] = specialty_no
        user_info["grade"] = grade
        user_info["class_no"] = class_no
        user_info["dorm_address"] = dorm_address
        re_data = {}
        for key, val in user_info.items():
            if val:
                val = str(val)
                if val == "无":
                    val = None
                val = trim_all(val)
            else:
                val = None
            re_data[key] = val
        with open("html/%s.html" % student_id, 'w') as f:
            f.write(info_page)
        return re_data
