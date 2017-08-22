# coding:utf-8
from captcha.base_captcha import BaseCaptcha
from config import local_config

PIC_PATH = local_config.get_value("CAPTCHA", "XGW_PATH")


class XGWCaptcha(BaseCaptcha):
    """
    学工网登录验证码识别类
    """
    def __init__(self, pic_name, threshold=100, pic_dir=PIC_PATH):
        super(XGWCaptcha, self).__init__(pic_name, threshold, pic_dir)
        pass


if __name__ == '__main__':
    path = '1.png'
    t = XGWCaptcha(path)
    print(t.get_verify())
