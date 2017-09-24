# coding:utf-8
from re import findall as re_findall
import socket
import ssl


def get_cookies():
    try:
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # http
        s = ssl.wrap_socket(socket.socket())  # https

        s.connect(('ipcrs.pbccrc.org.cn', 443))
        s.send(b'''GET / HTTP/1.1
Host: ipcrs.pbccrc.org.cn
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1

''')

        raw_content = b""
        buf = s.recv(1024)
        while len(buf):
            raw_content += buf
            buf = s.recv(1024)
        s.close()
        content = raw_content.decode("gbk")
        cookies = re_findall("Set-Cookie:([\s\S]+?);", content)
        cookie_dic = {cookie.split("=")[0].strip(): cookie.split("=")[1].strip() for cookie in cookies}
        return cookie_dic
    except Exception as e:
        return {}

if __name__ == '__main__':
    get_cookies()
