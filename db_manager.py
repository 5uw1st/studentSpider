# coding:utf-8
import redis
import pymongo
from pymongo.errors import ConnectionFailure

from config import LocalConfig

cf = LocalConfig()


def catch_mongo_except(func):
    """
    mongo错误处理装饰器
    :param func:
    :return:
    """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionFailure:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)

    return decorator


class MongoDB(object):
    """
    mongodb数据库管理
    """
    def __init__(self, db_name, table):
        option = "DB_MONGODB"
        self.__host = cf.get_value(option, "HOST")
        self.__port = cf.get_value(option, "PORT")
        self.__username = cf.get_value(option, "USERNAME")
        self.__password = cf.get_value(option, "PASSWORD")

        self.mongo_client = pymongo.MongoClient(self.__host, self.__port, connect=False)
        self.db = self.mongo_client[db_name]

        username = self.__username
        password = self.__password
        if username and password:
            self.db.authenticate(username, password)

        self.table = self.db[table]

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.mongo_client.close()
        return False

    @catch_mongo_except
    def getOne(self, **kwargs):
        result = self.table.find_one(kwargs.get("filter"), kwargs.get("fields"))
        return result if result else None

    @catch_mongo_except
    def getAll(self, **kwargs):
        result = self.table.find(kwargs.get("filter"), kwargs.get("fields"))

        sort = kwargs.get("sort")
        if sort is not None:
            result = result.sort(sort)
        limit = kwargs.get("limit")
        if limit is not None:
            result = result.limit(limit)
        skip = kwargs.get("skip")
        if skip is not None:
            result = result.skip(skip)

        return result

    @catch_mongo_except
    def distinct(self, key):
        return self.table.distinct(key)

    @catch_mongo_except
    def count(self, **kwargs):
        return self.table.count(kwargs.get("filter"))

    @catch_mongo_except
    def insertOne(self, value):
        return self.table.insert_one(value)

    @catch_mongo_except
    def updateOne(self, filter, update, upsert=False):
        return self.table.update_one(filter, update, upsert=upsert)

    @catch_mongo_except
    def deleteOne(self, **kwargs):
        return self.table.delete_one(kwargs.get("filter"))

    @catch_mongo_except
    def deleteMany(self, **kwargs):
        return self.table.delete_many(kwargs.get("filter"))

    @catch_mongo_except
    def aggregate(self, **kwargs):
        return self.table.aggregate(kwargs.get("pipeline"))

    @catch_mongo_except
    def changeTable(self, name):
        self.table = self.db[name]

    @catch_mongo_except
    def close(self):
        self.mongo_client.close()


class RedisManage(object):
    """
    redis管理
    """
    def __init__(self):
        option = "DB_REDIS"
        self.__host = cf.get_value(option, "HOST")
        self.__port = cf.get_value(option, "PORT")
        self.__db = cf.get_value(option, "DB_NAME")
        self.conn = None

    def get_conn(self):
        if not self.conn:
            self.conn = redis.Redis(host=self.__host, port=self.__port, db=self.__db)
        return self.conn
