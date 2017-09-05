#coding:utf-8
import redis
import random
#from shebao.bootstrap import Env #里面库文件 可以引用 全局操作类 在Env中引用CRedis类需要注意 循环引用
class CRedis(object):
 
    #注意如果使用kwargs 则可以使用kwargs['port']来取值
    def __init__(self, hosts, port, timeout):
        
        self._hosts = hosts
        self._port  = port
        self._db    = 0
        self._socket_timeout = float(timeout)
        self._connect = False
        
 
    def connect(self):
        
        #self._connect = False;
       
       
       
        hosts = self._hosts[:] #深度复制
        random.shuffle(hosts)
        
        while (len(hosts) and False == self._connect):
            host = hosts.pop()
            try:
                #(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)
                self.r = redis.StrictRedis(host = host, port = self._port, db = self._db, socket_timeout=self._socket_timeout)
                self._connect = True
            except Exception as ex:
                print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args)
                #raise Exception(u"connect to redis error!", ex.args)
                                
        if False == self._connect:
            raise Exception("connect to redis error !", "hosts:{0} port:{1}".format(self._hosts, self._port));
        #Env.get_logger().info(self._connect)
        
        
    #1. strings 类型及操作
    #设置 key 对应的值为 string 类型的 value
    def set(self, key, value):
        try:
            
            self.connect()
            return self.r.set(key, value)
        except Exception as ex:
            print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args)
            raise Exception(u"set key error!", key, value)
        
 
    #设置 key 对应的值为 string 类型的 value。如果 key 已经存在,返回 0,nx 是 not exist 的意思
    def setnx(self, key, value):
                
        self.connect()
        
        return self.r.setnx(key, value)
 
    #设置 key 对应的值为 string 类型的 value,并指定此键值对应的有效期
    def setex(self, key, time, value):
        self.connect()
       
        return self.r.setex(key, time, value)
 
    #设置指定 key 的 value 值的子字符串
    #setrange name 8 gmail.com
    #其中的 8 是指从下标为 8(包含 8)的字符开始替换
    def setrange(self, key, num, value):
        self.connect()
        return self.r.setrange(key, num, value)
 
    #获取指定 key 的 value 值的子字符串
    def getrange(self, key, start ,end):
        self.connect()
        return self.r.getrange(key, start, end)
 
    #mget(list)
    def get(self, key):
        self.connect()
        if isinstance(key, list):
            return self.r.mget(key)
        else:
            return self.r.get(key)
 
    #删除
    def remove(self, key):
        self.connect()
        return self.r.delete(key)
 
    #自增
    def incr(self, key, default = 1):
        self.connect()
        if (1 == default):
            return self.r.incr(key)
        else:
            return self.r.incr(key, default)
 
    #自减
    def decr(self, key, default = 1):
        self.connect()
        if (1 == default):
            return self.r.decr(key)
        else:
            return self.r.decr(key, default)
 
    #2. hashes 类型及操作
    def hexists(self, key, h_key):
        self.connect()
        return self.r.hexists(key, h_key)
    
    #根据email获取session信息
    def hget(self, key, h_key):
        self.connect()
        return self.r.hget(key, h_key)
 
    #以email作为唯一标识，增加用户session
    def hset(self, key, h_key, content):
        self.connect()
        return self.r.hset(key, h_key, content)
 
    #获取哈希表中的所有数据
    def hgetall(self, key):
        self.connect()
        return self.r.hgetall(key)
 
    #删除hashes
    def hdel(self, name, key = None):
        self.connect()
        if(key):
            return self.r.hdel(name, key)
        return self.r.hdel(name)
 
    #清空当前db
    def clear(self):
        self.connect()
        return self.r.flushdb()
 
    #3、lists 类型及操作
    #适合做邮件队列
    #在 key 对应 list 的头部添加字符串元素
    def lpush(self, key ,value):
        self.connect()
        return self.r.lpush(key, value)
 
    #从 list 的尾部删除元素,并返回删除元素
    def lpop(self, key):
        self.connect()
        return self.r.plush(key)
 
if __name__ == '__main__':
 
    try:
    
        import ConfigParser
        import os
        config = ConfigParser.ConfigParser();
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        conf_file = os.path.join(base_path, "confs/dev.ini")    
        config.read(conf_file)
        hosts = config.get('redis', 'hosts').split(",")
        port  = config.get('redis', 'port')
        timeout = config.get('redis', 'timeout')
        print hosts
       # print port
        #print timeout
        r = CRedis(hosts=hosts, port=port, timeout=timeout)
        import datetime;
        now = datetime.datetime.now();
        print 'now:{0}'.format(now);
        time = 5;
        #r = redis.StrictRedis(host='10.46.139.39',port=6379)
        r.setex('t', time, now);
        value = r.get('t');
        r.lpush('t1',now);
        r.lpush('t1', now)
        print value;
    except Exception as ex:
        print ex