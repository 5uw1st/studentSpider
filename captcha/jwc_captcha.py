# coding:utf-8
from captcha.base_captcha import BaseCaptcha
from config import local_config

PIC_PATH = local_config.get_value("CAPTCHA", "JWC_PATH")


class JWCCaptcha(BaseCaptcha):
    """
    教务处登录验证码识别类
    """
    def __init__(self, pic_name, threshold=165, pic_dir=None):
        super(JWCCaptcha, self).__init__(pic_name, threshold, pic_dir)
        pass

    def _binaryzation(self):
        """
        二值化, 可重写
        :return:
        """
        if self._table:
            pass
        for i in range(256):
            if self._threshold - 30 < i < self._threshold + 30:
                self._table.append(0)
            else:
                self._table.append(1)


if __name__ == '__main__':
    path = '22.jpg'
    t = JWCCaptcha(path)
    print(t.get_verify())
