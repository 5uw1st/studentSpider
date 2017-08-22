# coding:utf-8
try:
    import ConfigParser as cf
except:
    import configparser as cf
import os


class OverwriteConfig(cf.ConfigParser):
    def __init__(self, defaults=None):
        cf.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


class LocalConfig(object):
    def __init__(self, path="config.conf"):
        self.__cf = OverwriteConfig()
        self.__base_path = os.path.dirname(__file__)
        self.__name = os.path.join(self.__base_path, path)
        self.__cf.read(self.__name)

    def get_value(self, section, key):
        return self.__cf.get(section, key)

    def set_value(self, config_info):
        section = config_info['section']
        key = config_info['key']
        value = config_info['value']
        sections = self.__cf.sections()
        f = open(self.__name, 'w')
        if section not in sections:
            self.__cf.add_section(section)
        try:
            self.__cf.set(section, key, value)
            self.__cf.write(f)
        except:
            return False
        else:
            return True
        finally:
            f.close()

local_config = LocalConfig()
