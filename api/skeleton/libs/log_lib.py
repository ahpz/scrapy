# -*- coding: utf-8 -*-
# 日志记录模块

import logging
import time
import os
import json
import sys
class CLog(object):
    """ 日志操作模块 """
    
    def __init__(self, log_path, token):
        if (False == os.path.exists(log_path)):
            os.mkdir(log_path);
        self._log_file_path = log_path
        self._token    = token #通常用来区分模块的
        #self._log_id = time.strftime("%Y%m%d",time.localtime())
        
    #寻找调用Env.get_logger 的文件名和行号
    def _get_format(self):
        #获取调用者信息的文件名和行号 模拟logging 实现
        pass
        #rv = "(unknown file)", 0, "(unknown function)" #定义了元组的简单方式
        rv  = u"(unknown file)", 0
        try:
            f = sys._getframe()
            co = f.f_code
            src_file = os.path.normcase(co.co_filename)   #当前的文件名     
            """process thread 充当日志ID"""
            first = True;
            fmt = u'%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(name)s - %(process)d#%(thread)d - %(message)s'
            while hasattr(f, "f_code"):
                co = f.f_code
                filename = os.path.normcase(co.co_filename)
                if filename == src_file:
                    #print "filename:{0}".format(filename)
                    f = f.f_back
                    continue
                
                if first == True:
                    first=False;
                    continue;
                
                fmt = '%(asctime)s - {0}:{1} - %(levelname)s - %(name)s - %(process)d#%(thread)d - %(message)s'.format(os.path.basename(co.co_filename),f.f_lineno);
                break
                              
        except Exception as ex:
            sys.stdout.write(u"{0}:{1} Exception:{2} \n".format(__file__, sys._getframe().f_lineno, ex)) #有缓冲的 积累到一定大小则直接输出 多线程下是安全的
            fmt = '%(asctime)s - unknow file:unknow line - %(levelname)s - %(name)s - %(process)d#%(thread)d - %(message)s'
            pass
            
        return fmt
                
        
        #使用内部logging 
        #这里要求 args 中每个参数都是字符串 否则会出差 后期优化
    def debug(self, *args, **kwargs):
        pass
        log_file_name = time.strftime("%Y%m%d",time.localtime())
        log_file = os.path.join(self._log_file_path, log_file_name)
        fh = logging.FileHandler(log_file) # 实例化handler   
        #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(name)s - %(message)s'  
        fmt  = self._get_format()
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)      # 为handler添加formatter  
        
        message = '';
        #reload(sys);
        #sys.setdefaultencoding('utf-8');
        if len(args) > 0 :
            message = u"{0} {1}".format(message, json.dumps(args)) #如果元组args只有一个可变参数test 则会打印 ('test',) 格式
        if len(kwargs) > 0 :
            message = u"{0} {1}".format(message, json.dumps(kwargs))
        logger = logging.getLogger(self._token)    # 获取名为tst的logger  
        logger.addHandler(fh)           # 为logger添加handler  
        logger.setLevel(logging.DEBUG)   
        logger.debug(message)
        logger.removeHandler(fh)
        
    def info(self, *args, **kwargs):
        pass
        log_file_name = time.strftime("%Y%m%d",time.localtime())
        log_file = os.path.join(self._log_file_path, log_file_name)
        fh = logging.FileHandler(log_file) # 实例化handler   
        #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(name)s - %(message)s' 
        fmt  = self._get_format()
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)      # 为handler添加formatter  
        message = '';
        if len(args) > 0 :
            message = u"{0} {1}".format(message, json.dumps(args)) #如果元组args只有一个可变参数test 则会打印 ('test',) 格式
        if len(kwargs) > 0 :
            message = u"{0} {1}".format(message, json.dumps(kwargs))
       
        logger = logging.getLogger(self._token)    # 获取名为tst的logger  
        logger.addHandler(fh)           # 为logger添加handler  
        logger.setLevel(logging.INFO)   
        logger.info(message) 
        logger.removeHandler(fh)
        
    def warning(self, *args, **kwargs):
        pass
        log_file_name = time.strftime("%Y%m%d",time.localtime())
        log_file = os.path.join(self._log_file_path, log_file_name)
        log_file = log_file + ".wf"
        fh = logging.FileHandler(log_file) # 实例化handler   
        #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(name)s - %(message)s'  
        fmt  = self._get_format()
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)      # 为handler添加formatter  
        
        message = '';
        if len(args) > 0 :
            message = u"{0} {1}".format(message, json.dumps(args)) #如果元组args只有一个可变参数test 则会打印 ('test',) 格式
        if len(kwargs) > 0 :
            message = u"{0} {1}".format(message, json.dumps(kwargs))
        logger = logging.getLogger(self._token)    # 获取名为tst的logger  
        logger.addHandler(fh)           # 为logger添加handler  
        logger.setLevel(logging.WARN)   
        logger.warn(message)
        logger.removeHandler(fh) # 和 addHandler 对应 否则 在频繁输出日志时 会出现 too many open files
        
    def error(self, *args, **kwargs):
        pass
        log_file_name = time.strftime("%Y%m%d",time.localtime())
        log_file = os.path.join(self._log_file_path, log_file_name)
        log_file = log_file + ".wf"
        fh = logging.FileHandler(log_file) # 实例化handler   
        #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(name)s - %(message)s'  
        fmt  = self._get_format()
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)      # 为handler添加formatter  
        
        message = '';
        
        if len(args) > 0 :
            message = u"{0} {1}".format(message, json.dumps(args)) #如果元组args只有一个可变参数test 则会打印 ('test',) 格式
        if len(kwargs) > 0 :
            message = u"{0} {1}".format(message, json.dumps(kwargs))
        logger = logging.getLogger(self._token)    # 获取名为tst的logger  
        logger.addHandler(fh)           # 为logger添加handler  
        logger.setLevel(logging.ERROR)   
        #print "message:{0}".format(message)
        logger.error(message)  
        logger.removeHandler(fh)
    
if  __name__ == "__main__":
    obj_log = CLog(log_path = "./", token = "test");
    obj_log.debug('test');
    obj_log.debug('test',m="test2")
    obj_log.debug(u'中');
    
    #注意 python 自带的logging 可以自己创建文件
    #2016-03-10 19:36:02,720 - log_lib.py:32 - test - ["test"] {}
    #2016-03-10 19:36:02,720 - log_lib.py:32 - test - ["test"] {"m": "test2"}
    #2016-03-10 19:36:02,720 - log_lib.py:32 - test - ["test"] {"m": "test2"}
    
