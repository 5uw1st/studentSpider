# coding:utf-8
from re import search as re_search

from requests import get as http_get, post as http_post

from my_socket import get_cookies


def handle_exception(show_error=True):
    """
    错误处理装饰器
    :param show_error:
    :return:
    """
    def _handle(func):
        def __handle(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                func_name = func.__name__
                if show_error:
                    print("[-]func:%s, ERROR:%s" % (func_name, str(e)))
                else:
                    print("[-]func:%s,--->ERROR" % func_name)
                return
        return __handle
    return _handle


@handle_exception()
def get_tag_value(content, tag_name, default_value=""):
    """
    获取标签值
    :param content:
    :param tag_name:
    :param default_value:
    :return:
    """
    pattern = '<input[\s\S]+?name="%s"\s*value="([^"]+)"' % tag_name
    res = re_search(pattern, content)
    if res is not None:
        return res.group(1)
    else:
        return default_value


@handle_exception()
def http_request(url, method="GET", is_img=False, get_cookies=False, cookies=None,
                 headers=None, timeout=10, referer=None, data=None, charset=None):
    """
    处理HTTP请求
    :param url:
    :param method:
    :param is_img:
    :param get_cookies:
    :param cookies:
    :param headers:
    :param timeout:
    :param referer:
    :param data:
    :param charset:
    :return:
    """
    if not url and isinstance(url, str):
        raise TypeError
    if referer is None:
        referer = "https://ipcrs.pbccrc.org.cn/"
    if headers is None:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Host": "ipcrs.pbccrc.org.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/60.0.3112.113 Safari/537.36",
            "Referer": referer,
        }
    if method == "GET":
        response = http_get(url, cookies=cookies, timeout=timeout, headers=headers, verify=False)
    else:
        response = http_post(url, cookies=cookies, timeout=timeout, headers=headers, data=data, verify=False)
    if response.status_code == 200:
        if is_img:
            content = response.content
        else:
            content = response.content
            if response.text.find("charset=gbk") >= 0:
                content = content.decode("gbk")
            elif response.text.find("charset=utf-8") >= 0:
                content = content.decode("utf-8")
            else:
                if charset is not None:
                    content = content.decode(charset)
                else:
                    content = response.text
        print("下载网页成功: %s" % url)
        if get_cookies:
            cookies = response.cookies
            return [content, cookies]
        return content
    else:
        print("请求失败：%d" % response.status_code)
        return None


class PbccLogin(object):
    """
    人行征信登录
    """

    def __init__(self, username, password):
        self._index_url = "https://ipcrs.pbccrc.org.cn/"
        self._login_url = "https://ipcrs.pbccrc.org.cn/login.do?method=initLogin"
        self._post_url = "https://ipcrs.pbccrc.org.cn/login.do"
        self._username = username
        self._password = password
        self.cookies = {}
        self.__code_file = "code.jpg"

    @handle_exception()
    def do_login(self):
        """
        登录
        :return:
        """
        post_data = self.__ready_post_params()
        if not post_data:
            print("[-]准备请求参数失败")
            return False
        cookies = get_cookies()
        page = http_request(self._post_url, method="POST", data=post_data, get_cookies=True, cookies=cookies)
        if page and page[0].find(">新手导航<") >= 0:
            self.cookies = page[1]
            return True
        return False

    @handle_exception()
    def __ready_post_params(self):
        """
        准备请求参数
        :return:
        """
        login_page = http_request(self._login_url)
        token_name = "org.apache.struts.taglib.html.TOKEN"
        verify_code = self.__get_verify_code(login_page)
        if not verify_code:
            print("[+]验证码获取失败")
            return
        post_data = {
            token_name: get_tag_value(login_page, token_name),
            "method": get_tag_value(login_page, "method"),
            "date": get_tag_value(login_page, "method"),
            "loginname": self._username,
            "password": self._password,
            "_@IMGRC@_": verify_code,
        }
        return post_data

    @handle_exception()
    def __get_verify_code(self, page):
        """
        获取验证码
        :param page:
        :return:
        """
        res = re_search('<img src="([^"]+)"\s*id="imgrc', page)
        if res is not None:
            yzm_url = self._index_url + res.group(1)
            img_content = http_request(yzm_url, is_img=True)
            with open(self.__code_file, "wb") as f:
                f.write(img_content)
            while True:
                code = input("[+]请输入验证码：")
                if code.strip():
                    return code.strip()
                else:
                    print("[+]验证码输入有误, 请重新输入")

        else:
            print("[-]获取验证码URL失败")
            return None

if __name__ == '__main__':
    user = "westblog"
    pwd = "19940807Qq"
    pbcc = PbccLogin(user, pwd)
    isSucc = pbcc.do_login()
    if isSucc:
        print(pbcc.cookies)
    else:
        print("登录失败")
