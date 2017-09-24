# coding:utf-8
import sys
import os
from PIL import Image, ImageDraw
import cv2


def get_threshold(path):
    base_path = os.getcwd()
    path = os.path.join(base_path, path)
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)  # 方法选择为THRESH_OTSU
    return [ret, th]


def getPixel(image, x, y, G, N):
    """
    二值判断,如果确认是噪声,用该点的上面一个点的灰度进行替换
    该函数也可以改成RGB判断的,具体看需求如何
    :param image:
    :param x:
    :param y:
    :param G:
    :param N:
    :return:
    """
    L = image.getpixel((x, y))  # 0:黑色 1:白色
    if L == 1:
        return
    if L == G:
        L = True
    else:
        L = False

    nearDots = 0
    if L == (image.getpixel((x - 1, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1, y)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1, y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x, y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y + 1)) > G):
        nearDots += 1

    if nearDots > N:
        return image.getpixel((x, y - 1))
    else:
        return None


def clearNoise(image, G, N, Z):
    """
    # 降噪
    # 根据一个点A的RGB值，与周围的8个点的RBG值比较，设定一个值N（0 <N <8），当A的RGB值与周围8个点的RGB相等数小于N时，此点为噪点
    # G: Integer 图像二值化阀值
    # N: Integer 降噪率 0 <N <8
    # Z: Integer 降噪次数
    # 输出
    #  0：降噪成功
    #  1：降噪失败
    :param image:
    :param G:
    :param N:
    :param Z:
    :return:
    """
    draw = ImageDraw.Draw(image)

    for i in range(0, Z):
        for x in range(1, image.size[0] - 1):
            for y in range(1, image.size[1] - 1):
                color = getPixel(image, x, y, G, N)
                if color != None:
                    draw.point((x, y), color)
    return draw


def get_crop_imgs(img):
    """
    按照图片的特点,进行切割,这个要根据具体的验证码来进行工作.
    :param img:
    :return:
    """
    child_img_list = []
    x_list = []
    for x in range(1, img.size[0] - 1):
        count = 0
        for y in range(1, img.size[1] - 1):
            pix = img.getpixel((x, y))  # 0:黑色 1:白色
            if pix == 0:
                count += 1
        if count >= 2:
            x_list.append(x)
    x_list.append(0)
    first = x_list[0]
    s_len = 0
    y = 1
    m = 1
    for k in range(1, len(x_list)):
        if first+m == x_list[k]:
            s_len += 1
            m += 1
        else:
            if s_len >= 3:
                if s_len >= 26:
                    child_img = img.crop((first, y, first + s_len//2, y + 28))
                    child_img_list.append(child_img)
                    child_img = img.crop((first + s_len//2, y, first + s_len, y + 28))
                    child_img_list.append(child_img)
                else:
                    child_img = img.crop((first, y, first+s_len, y + 28))
                    child_img_list.append(child_img)
            first = x_list[k]
            s_len = 0
            m = 1
    return child_img_list


if __name__ == '__main__':
    path = r"D:\workspace\studentSpider\captcha\img\jwc\a256b1b1afedb80836f494f9d0e19a45.png"
    print(get_threshold(path))
