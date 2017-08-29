# coding:utf-8
from captcha.base_captcha import BaseCaptcha
from config import local_config

from captcha import handle

PIC_PATH = local_config.get_value("CAPTCHA", "JWC_PATH")


class JWCCaptcha(BaseCaptcha):
    """
    教务处登录验证码识别类
    """
    def __init__(self, pic_name, threshold=204, pic_dir=None):
        super(JWCCaptcha, self).__init__(pic_name, threshold, pic_dir)
        pass

    def _binaryzation(self):
        """
        二值化, 可重写
        :return:
        """
        if self._table:
            return
        pic_path = self._pic_name
        ret, th = handle.get_threshold(pic_path)
        self._threshold = ret
        for i in range(256):
            if self._threshold >= i:
                self._table.append(0)
            else:
                self._table.append(1)

    def _clear_noise(self, img):
        """
        图片降噪
        :return:
        """
        g = 0
        n = 6
        z = 90
        return handle.clearNoise(img, g, n, z)

    def _get_crop_imgs(self, img):
        child_imgs = handle.get_crop_imgs(img)
        for index, i in enumerate(child_imgs):
            i.save("cut_%d.jpg" % (index+1))


if __name__ == '__main__':
    path = '22.jpg'
    t = JWCCaptcha(path)
    print(t.get_verify())
