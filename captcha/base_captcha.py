# coding:utf-8
import sys
import os

from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import *


class BaseCaptcha(object):
    """
    验证码识别基类
    """
    def __init__(self, pic_name, threshold=140, pic_dir=None):
        self._pic_name = pic_name
        self._threshold = threshold
        self._table = []
        self._pic_dir = pic_dir
        self.__curdir = os.getcwd()
        self._rep_dic = {
            '?': '2',
        }

    def _set_rep_dict(self, rep_dic):
        """
        设置替换表
        :param rep_dic:
        :return:
        """
        self._rep_dic = rep_dic

    def _binaryzation(self):
        """
        二值化, 可重写
        :return:
        """
        if self._table:
            return
        for i in range(256):
            if i < self._threshold:
                self._table.append(0)
            else:
                self._table.append(1)

    def __turn_dir(self):
        """
        切换到图片目录
        :return:
        """
        try:
            if self._pic_dir is None:
                pic_dir = "./img/jwc/"
            else:
                pic_dir = self._pic_dir
            if not os.path.exists(pic_dir):
                return False
            os.chdir(pic_dir)
            return True
        except Exception as e:
            return False

    def get_verify(self):
        """
        验证码识别
        :return:
        """
        text = "FAIL"
        # 切换目录
        if not self.__turn_dir():
            return "FAIL_DIR"

        # 二值化
        self._binaryzation()
        try:
            # 打开图片
            pic_name = self._pic_name.split("\\")[-1]
            im = Image.open(pic_name)
            # 转化到灰度图
            imgry = im.convert('L')
            # 保存图像
            imgry.save('g_' + pic_name)

            # 二值化，采用阈值分割法，threshold为分割点
            out = imgry.point(self._table, '1')
            out.save('b_' + pic_name)
            # 降噪
            self._clear_noise(out)
            out.save('n_' + pic_name)
            # 切割
            self._get_crop_imgs(out)

            # 识别
            text = image_to_string(out)
            # 识别对吗
            text = text.strip()
            text = text.upper()
            for r in self._rep_dic:
                text = text.replace(r, self._rep_dic[r])
                # out.save(text+'.jpg')
        except Exception as e:
            text = "FAIL_ERR"
        finally:
            os.chdir(self.__curdir)  # 切回原目录
            return text

    def _clear_noise(self, img):
        """
        图片降噪
        :return:
        """
        raise NotImplemented

    def _get_crop_imgs(self, img):
        """
        分割图片
        :param img:
        :return:
        """
        raise NotImplemented

    def _get_path(self):
        """
        获取图片绝对路径
        :return:
        """
        pass
