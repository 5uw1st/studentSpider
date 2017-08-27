# coding:utf-8
from threading import Thread
import time

from spider.xg_spider import XGSpider
from spider.jwc_spider import JWCSpider
from db_manager import MongoDB, RedisManage
from utils import log, handle_exception
from config import local_config

cf = local_config
jwc = JWCSpider()
xgw = XGSpider()
db_name = cf.get_value("DB_MONGODB", "DB_NAME")
id_table = cf.get_value("DB_MONGODB", "ID_TABLE")
info_table = cf.get_value("DB_MONGODB", "INFO_TABLE")
id_mongo = MongoDB(db_name, id_table)
info_mongo = MongoDB(db_name, info_table)
redis = RedisManage().get_conn()
id_key = cf.get_value("DB_REDIS", "ID_KEY")
init_redis_flag = cf.get_value("USER", "INIT_REDIS")
user = cf.get_value("USER", "USERNAME")
pwd = cf.get_value("USER", "PASSWORD")


def init_redis():
    """
    将数据初始化到redis
    :return:
    """
    pipeline = [{
        "$project": {
            "_id": 0,
            "id": "$_id"
        }
    }]
    infos = id_mongo.aggregate(pipeline=pipeline)
    if infos:
        with redis.pipeline() as rpipe:
            for info in infos:
                rpipe.lpush(id_key, info["id"])
            rpipe.execute()
            log("初始化redis数据完成")
            return True
    else:
        log("无任何数据")
    return False


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
            try:
                info.update({"password": True, "_id": info["id"]})
                info.pop("id")
                id_mongo.insertOne(info)
            except Exception as e:
                continue
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
    is_succ = False
    pwd_list = [password, "12345678", "123456"]
    for p in pwd_list:
        is_succ = xgw.login(username, p)
        if is_succ:
            password = p
            break
    if is_succ:
        user_info = xgw.get_user_info()
        user_info.update({"img_url": "", "_id": user_info["student_id"]})
        user_info.pop("student_id")
        info_mongo.insertOne(user_info)
        log("用户[%s]的信息获取完成" % username)
        log("INFO:%s" % str(user_info))
        id_mongo.updateOne({"_id": username.decode()}, {"$set": {"password": password.decode()}})
    else:
        id_mongo.updateOne({"_id": username.decode()}, {"$set": {"password": False}})
        log("登录失败，未获取到任何信息 -->%s" % username)


def run():
    """
    开始运行
    :return:
    """
    # 获取学号信息并保存
    handle_id_info()
    if init_redis_flag == "1":
        # 从mongodb数据库初始化数据到redis
        if not init_redis():
            return

    while True:
        # 取出一条记录
        user_id = redis.lpop(id_key)
        if user_id:
            # 获取学生信息并保存
            get_user_info(user_id, user_id)
        else:
            break


if __name__ == '__main__':
    run()

