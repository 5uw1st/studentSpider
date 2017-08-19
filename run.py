# coding:utf-8

from spider.xg_spider import XGSpider
from spider.jwc_spider import JWCSpider


def run():
    """
    开始运行
    :return:
    """
    # 从数据库初始化数据到redis
    pass
    # 取出一条记录
    pass
    # 尝试登录
    pass
    # 成功后获取信息
    pass
    # 保存到mongodb

    user = "2013123069"
    pwd = "19940807qQ"
    # t = XGSpider()
    t = JWCSpider()
    isSucc = t.login(user, pwd)
    print(isSucc)


if __name__ == '__main__':
    run()
