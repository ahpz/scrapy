# -*- coding: utf-8 -*-

#添加的 20130317 pengzhi add
import sys
import os
import ConfigParser
import sys
#print __file__
#print sys.path
from libs.log_lib import CLog
#from shebao.libs.redis_lib import CRedis #这里会导致循环引用



#添加当前路径到模块搜索路径中
#sys.path.append(os.path.realpath(__file__))

class Env(object):      
    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) #类变量 realpath 消除外链接
    env       = os.getenv('PYTHON_MAP_ENV')
    pass
    @classmethod
    def get_config(cls):
        #类方法 
        pass
        if not hasattr(cls, '_config'):#已经通过 _init_.py 测试 类单例模式
            config = ConfigParser.ConfigParser()
            #base_path   = os.path.dirname(os.path.realpath(__file__))
            #env = os.getenv('PYTHON_MAP_ENV')
            if cls.env is None: #未定义 此环境变量 则默认是 dev 线下环境配置
                cls.env = 'dev'
            conf_file   = os.path.join(cls.base_path, "confs/{0}.ini".format(cls.env)) #后期考虑根据python 脚步 配置设置
            config.read(conf_file)   
            cls._config = config
           
            
        return cls._config
     
    @classmethod
    def get_logger(cls):
        pass
        if not hasattr(cls, '_logger'):
            config   = cls.get_config();
            log_path = config.get('log', 'path')
            token    = config.get('log', 'token')
            cls._logger = CLog(log_path, token)
        return cls._logger
    
    @classmethod
    def output(cls, *args, **kwargs):
        #屏幕输出函数
        fmt = ''
        
        try:
            f = sys._getframe()
            co = f.f_code
            src_file = os.path.normcase(co.co_filename)   #当前的文件名     
            #寻找上一个文件名 和 行号
            while hasattr(f, "f_code"):
                co = f.f_code
                filename = os.path.normcase(co.co_filename) 
                if filename == src_file:
                    #print "filename:{0}".format(filename)
                    f = f.f_back
                    continue

                fmt = u"{0}:{1}".format(os.path.basename(co.co_filename), f.f_lineno);
                #print "fmt {0}".format(fmt)
                break
                                
        except Exception as ex:
            sys.stdout.write(u"{0}:{1} Exception:{2} \n".format(os.path.basename(__file__), sys._getframe().f_lineno, ex))
            fmt = u'unknow file:unknow line'
            pass        
        pass
        message = fmt;
        try:
            if len(args) > 0:
                #要求args 里面的每个参数 是字符串
                import json #ensure_ascii=False 保证中文输出正常
                message = u"{0} {1}\n".format(message, json.dumps(args)) #如果元组args只有一个可变参数test 则会打印 ('test',) 格式 json.dumps(args) 则转换成[test]
            if len(kwargs) > 0:
                import json
                message = u"{0} {1}\n".format(message, json.dumps(kwargs))
        except Exception as ex:
            pass
            sys.stdout.write(u"Exception:{0} \n".format(repr(ex)));
        except:
            sys.stdout.write("Other exception!\n")
        print message
    @classmethod    
    def get_redis_proxy(cls):
        from  libs.redis_lib import CRedis #保证不会循环引用 
        config   = cls.get_config();
       
        hosts = config.get('redis', 'hosts').split(",")
        port  = config.get('redis', 'port')
        timeout = config.get('redis', 'timeout')
        
        #print "get_redis_proxy :{0}".format(hosts)
        
        obj_redis_proxy = CRedis(hosts = hosts, port = port, timeout = timeout)
        return obj_redis_proxy
    @classmethod
    def get_db_proxy(cls, db = 'db'):
        from libs.mysql_lib import CMysql 
        config   = cls.get_config();
       
        hosts = config.get(db, 'hosts').split(",")
        port  = config.get(db, 'port')
        username = config.get(db, 'username')
        password = config.get(db, 'password')
        dbname   = config.get(db, 'dbname')
        
        #print "get_redis_proxy :{0}".format(hosts)
        
        obj_db_mysql = CMysql(hosts = hosts, port = port, username=username, password=password, dbname=dbname)
        
        return obj_db_mysql        
    @classmethod
    def get_mail_proxy(cls, mail = 'mail'):
        pass
        from libs.email_lib import CEmail
        config = cls.get_config()
               #注意smtp.baidu.com调用失败
        host   = config.get(mail, 'host')
        user   = config.get(mail, 'user')
        pwd    = config.get(mail, 'pwd')
        #mailfrom=config.get(mail, 'from')
        obj_mail_proxy = CEmail(host = host, user = user, passwd = pwd)
        return obj_mail_proxy 
    @classmethod
    def get_ftp_proxy(cls, ftp = 'ftp'):
        pass
        from libs.ftp_lib import CFtp
        config = cls.get_config()
        host   = config.get(ftp, 'host')
        #path   = config.get(ftp, 'path')
        user   = config.get(ftp, 'username')
        pwd    = config.get(ftp, 'password')
        obj_ftp_proxy = CFtp(ip = host, uname=user, pwd=pwd)
        return obj_ftp_proxy
        
    @classmethod
    def get_youtube_api(cls, conf = 'youtube'):
        pass
        from libs.youtube_lib import YoutubeAPI
        config = cls.get_config()
        key   = config.get(conf, 'key')
        youtube = YoutubeAPI({'key': key})
        return youtube
    @classmethod
    def get_youtube_proxy(cls):
        pass
        from libs.youtube_lib import CYoutube
        youtube = CYoutube()
        return youtube
        
   
    
    
    