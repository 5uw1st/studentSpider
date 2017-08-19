# coding:utf-8
import logging
import re
from urllib.parse import quote, unquote

from lxml.html import etree
from requests import session

from data_type import *

# logging.basicConfig(level=logging.DEBUG,
#                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                 datefmt='%Y-%m-%d %H:%M:%S')

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
logfile = './log/log.text'
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

# 第三步，再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

# 第四步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)


def log(msg, level=LOG_INFO, err_code=None):
    """
    打印日志
    :param msg:
    :param level:
    :param err_code:
    :return:
    """
    if err_code:
        msg = msg + " -->[ERROR_CODE:%d]" % err_code
    if level == LOG_CRITICAL:
        logger.log(logging.CRITICAL, msg)
    elif level == LOG_ERROR:
        logger.log(logging.CRITICAL, msg)
    elif level == LOG_WARNING:
        logger.log(logging.WARNING, msg)
    elif level == LOG_INFO:
        logger.log(logging.INFO, msg)
    else:
        logging.log(logging.DEBUG, msg)


def download(url, get_cookies=False, referer=None, is_img=False, data=None, headers=None, cookies=None, timeout=10):
    """
    下载网页
    :param url:
    :param get_cookies:
    :param referer:
    :param is_img:
    :param data:
    :param headers:
    :param cookies:
    :param timeout:
    :return:
    """
    try:
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/7.0)",
                "Connection": "Keep-Alive",
                "Accept": "text/html, application/xhtml+xml, */*",
                "Accept-Encoding": "gzip, deflate",
                "Referer": referer if referer is not None else url
            }
        s = session()
        if data is not None:
            # POST
            response = s.post(url, data=data, headers=headers, cookies=cookies, timeout=timeout)
        else:
            # GET
            response = s.get(url, headers=headers, cookies=cookies, timeout=timeout)
        if response.status_code == 200:
            if is_img:
                content = response.content
            else:
                content = response.text
            log("下载网页成功: %s" % url)
            if get_cookies:
                cookies = response.cookies
                return [content, cookies]
            return content
        else:
            return
    except Exception as e:
        log("下载网页异常:%s -->%s" % (url, str(e)), LOG_ERROR)
        return None


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
                if show_error:
                    log("ERROR:%s" % str(e), LOG_ERROR)
                else:
                    log("--->ERROR", LOG_ERROR)
                return
        return __handle
    return _handle


@handle_exception()
def xpath_match(html, xpath, get_one=True ,default=None):
    """
    XPATH匹配
    :param html:
    :param xpath:
    :param get_one:
    :param default:
    :return:
    """
    if isinstance(html, str):
        dom = etree.HTML(html)
    else:
        dom = html
    res = dom.xpath(xpath)
    if res and len(res) > 0:
        if get_one:
            return res[0]
        else:
            return res
    elif default:
        return default
    else:
        return


@handle_exception()
def reg_match(page, pattern, get_one=True, default=None):
    """
    正则匹配
    :param page:
    :param pattern:
    :param get_one:
    :param default:
    :return:
    """
    if get_one:
        res = re.findall(pattern, page)
    else:
        res = re.search(pattern, page)
        if res is not None:
            res = res.group(1)
    if res:
        return res
    elif default:
        return default
    else:
        return


@handle_exception()
def is_match(page, pattern):
    """
    是否匹配
    :param page:
    :param pattern:
    :return:
    """
    return re.search(pattern, page) is not None


@handle_exception()
def url_encode(url):
    """
    url编码
    :param url:
    :return:
    """
    return quote(url)


@handle_exception()
def url_decode(url):
    """
    url解码
    :param url:
    :return:
    """
    return unquote(url)


def trim_all(text, opt_list=None):
    """
    去除空格换行等字符
    :param text:
    :param opt_list:
    :return:
    """
    try:
        res = ""
        default_list = ["\n", "\r\n", "\t", "&nbsp;", "\xa0"]
        if opt_list is not None and isinstance(opt_list, list):
            default_list += opt_list
        for i in default_list:
            res = text.replace(i, "")
        res = re.sub("\s+", " ", res)
        res = res.strip()
        return res
    except Exception as e:
        log("转换字符串失败：%s" % str(e))
        return text


