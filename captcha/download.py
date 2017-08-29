# coding: utf-8

import requests
import uuid


def download_pic(url, path=None, headers=None, referer=None, timeout=10):
    """
    下载图片
    :param url:
    :param headers:
    :param referer:
    :param timeout:
    :return:
    """
    try:
        if headers is None:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Referer": referer if referer else "http://210.41.224.117/Login/xLogin/Login.asp",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
                "Cookie": "ASPSESSIONIDCQBATDCB=OLEPPCKBBCACOAGNALIONDMM",
                "Host": "210.41.224.117"
            }
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            if path is None:
                path = str(uuid.uuid1()) + ".jpg"
            with open(path, 'wb') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        return False


if __name__ == '__main__':
    url = "http://210.41.224.117/Login/xLogin/yzmDvCode.asp?k=401395&t=1503889731964"
    print(download_pic(url))