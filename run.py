# coding:utf-8
from threading import Thread
import time

from spider.xg_spider import XGSpider
from spider.jwc_spider import JWCSpider
from db_manager import MongoDB, RedisManage
from utils import log, handle_exception
from config import LocalConfig

cf = LocalConfig()
jwc = JWCSpider()
xgw = XGSpider()
db_name = cf.get_value("DB_MONGODB", "DB_NAME")
id_table = cf.get_value("DB_MONGODB", "ID_TABLE")
info_table = cf.get_value("DB_MONGODB", "INFO_TABLE")
id_mongo = MongoDB(db_name, id_table)
info_mongo = MongoDB(db_name, info_table)
redis = RedisManage().get_conn()
id_key = cf.get_value("DB_REDIS", "ID_KEY")
user = cf.get_value("USER", "USERNAME")
pwd = cf.get_value("USER", "PASSWORD")


def init_redis():
    """
    将数据初始化到redis
    :return:
    """
    pass


@handle_exception()
def handle_id_info():
    """
    获取学号信息，并保存
    :return:
    """
    # 登录教务处
    is_succ = jwc.login(user, pwd)
    if is_succ:
        id_list = jwc.get_student_info()
        for info in id_list:
            id_mongo.insertOne(info)
        log("所有信息获取并保存完成")
    else:
        log("登录失败，未获取到任何信息")


@handle_exception()
def get_user_info(username, password):
    """
    获取用户信息
    :param username:
    :param password:
    :return:
    """
    is_succ = xgw.login(username, password)
    if is_succ:
        user_info = xgw.get_user_info()
        info_mongo.insertOne(user_info)
        log("用户[%s]的信息获取完成" % username)
        log("INFO:%s" % str(user_info))
    else:
        log("登录失败，未获取到任何信息")


def run():
    """
    开始运行
    :return:
    """

    # 将学号信息写入mongodb
    pass
    # 从mongodb数据库初始化数据到redis
    pass
    # 取出一条记录
    pass
    # 尝试登录
    pass
    # 成功后获取信息
    pass
    # 保存到mongodb

    user = ""
    pwd = ""
    t = XGSpider()
    # t = JWCSpider()
    isSucc = t.login(user, pwd)
    if isSucc:
        print(t.get_user_info())


if __name__ == '__main__':
    run()
