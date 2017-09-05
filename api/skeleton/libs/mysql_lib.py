#coding:utf-8
import MySQLdb
import random
#继承object 保证该类是new-style类
import sys
import os
__author__ = 'pengzhi'
class CMysql(object):
    """ 连接MySQL数据库操作类 """
    # 三个单引号的注释 很强大 能够通过 __doc__属性返回
    #单/双下划线开头的函数或类不会被from module import *导入
    #双下划线开头的类成员函数/变量会被python内部改写，加上类名前缀。以避免与派生类同名成员冲突
    #单/双下划线都不能真正意义上阻止用户访问，只是module开发者与使用者之间的”约定”    
       
    
    #_connect = False
    #_conn    = None
    #_cur     = None #类变量 ！= self._connect
    
    #绑定类型 类变量
    TYPE_STR  = "%s"
    TYPE_CHAR = "%c"
    TYPE_NUM  = "%d"
    
    def __init__(self, hosts, port, username, password, dbname):
        #初始化函数
        self._hosts = hosts; #列表
        self._port  = port;
        self._username = username;
        self._password = password;
        self._dbname   = dbname
        self._connect  = False
        self._cur      = None
        self._conn     = None
        
    def connect(self):
        #初始化新建对象
        #random.shuffle(self._hosts);
        #self._connect = False;
        #grant all privileges on *.* to 'luoqinglin'@'170.20.140.15' identified by 'IijbQKV4oo' with grant option;# MySQL 返回的查询结果为空 (即零行)。
         
        #flush privileges;# MySQL 返回的查询结果为空 (即零行)。        
        hosts = self._hosts[:] #深度复制
        random.shuffle(hosts)
        while (len(hosts) and False == self._connect):
            try:
                host = hosts.pop();
                #print self._hosts;
                #print "user:{0} passwd:{1} db:{2}".format(self._username, self._password, self._dbname) 
                self._conn = MySQLdb.connect(host=host,user=self._username,passwd=self._password,db=self._dbname, port=int(self._port), charset='utf8',);
                #self._conn.select_db(self._dbname)
                
                self._cur = self._conn.cursor(cursorclass = MySQLdb.cursors.DictCursor) #返回结果集 为字典类型 也可以在 connect中配置
                self._connect = True;
                #self._cur.execute('SET NAMES utf-8');
            except MySQLdb.Error as ex:
                print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args)
                #print u"[{0}:{1}] Exception:{2} {3}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args[0], ex.args[1])
               
                
            except Exception as ex: #所有异常 基类
                #print u"[{0}:{1}] Exception:{2} {3}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args[0], ex.args[1])
                print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args)
                
            except:
                print u"[{0}:{1}] Exception:unknow".format(os.path.basename(__file__), sys._getframe().f_lineno)
        if False == self._connect:
            raise Exception(u"connect to db error !", u"hosts:({0}) port:{1}".format(self._hosts, self._port));
              
        
    """execute(self, query, args)"""
    def execute(self, *args):
        pass
        iRet = 0;
        try:
            self.connect();
           
            if len(args) > 1 :
                #print "len(args):{0} args:{1}".format(len(args), args)
                sql = args[0] #元组和列表类似 只不过元组不能修改
                vals = args[1]
                iRet = self._cur.execute(sql, vals) #cursor.execute("select * from writers where id = %s", "3") 预编译写法
            elif len(args) == 1:
                sql = args[0] #元组和列表类似 只不过元组不能修改
                iRet = self._cur.execute(sql)
            else:
                raise Exception(u"No arg for execute!")
            
            
        except MySQLdb.Error as ex:
            print "MySQLdb.Error :{0}".format(ex)
            #args[0] 错误码 args[1] 错误提示字符串
            raise Exception(u'execute error !', ex.args) #message != args[0]
        finally:
            pass
        
        return iRet
    
    '''执行多个sql语句 只不过每个语句的参数值不同'''
    def execute_many(self, *args):
        pass
        iRet = 0;
        try:
            self.connect()
            if len(args) > 1:
                sql = args[0]
                dict_vals = args[1]
                iRet = self._cur.executemany(sql, dict_vals)
            elif len(args) == 1:
                sql = args[0]
                iRet = self._cur.executemany(sql)
            else:
                raise Exception(u"No arg for execute_many!")
        except MySQLdb.Error as ex:
            print ex
            raise Exception(u'execute_many error !', ex.args)
            #Env.get_logger.error(ex)
        finally:
            pass
        return iRet;
        
    #cursor.execute("select * from writers where id = %s", "3") 预编译写法
    '''sql = "INSERT INTO EMPLOYEE(FIRST_NAME, \
       LAST_NAME, AGE, SEX, INCOME) \
       VALUES ('%s', '%s', '%d', '%c', '%d' )" % \
       ('Mac', 'Mohan', 20, 'M', 2000)'''   
    def fetch_one(self, sql, *args):
        pass
        self.connect()
        if len(args) > 0:
            self.execute(sql, args[0])
        else:
            self.execute(sql)
         
        return self._cur.fetchone()
    
    def fetch_all(self, sql, *args):
        pass
        self.connect()
        if len(args) > 0:
            self.execute(sql, args[0]);
        else:
            self.execute(sql)

        return self._cur.fetchall()
    
    #查询指定行数数据
    def fetch_many(self, sql, limit, *args):
        pass
        self.connect()
        if len(args) > 0:
            iRet = self.execute(sql, args[0])
        else:
            iRet = self.execute(sql)
        return self._cur.fetchmanay(limit) #指定函数的结果急
    
    def update(self, tb_name,list_field, list_value, str_condition):
        pass
        if len(list_field) != len(list_value):
            raise Exception(u"The field not equal value!", list_field, list_value)        
        self.connect()
        
        str_seg = '';
        for idx in range(len(list_field)):
            str_seg += u"`{0}` = '{1}',".format(list_field[idx], list_value[idx])
            
        str_seg = str_seg.rstrip(",")
        
        sql = u"update `{0}` set {1} where {2}".format(tb_name, str_seg, str_condition) # 
        #print sql
        iRet = self.execute(sql)
        self.commit()
        
        return iRet;
    #插入单个记录返回影响的行数
    #
    #
    # bind_type = ('%s' '%c' %d)
    def insert(self, tb_name, list_field, list_value, list_type = ()):
        pass
        if len(list_field) != len(list_value):
            raise Exception(u"The field not equal value!", list_field, list_value)
        
        self.connect()
       
        if len(list_type) == len(list_field):
            pass
            str_field = u'';
            str_type  = u'';
            for idx in range(len(list_field)):
                pass
                str_field += u",`{0}`".format(list_field[idx])
                str_type  += u",'{0}'".format(list_type[idx])
                #list_value[idx] = MySQLdb.escape_string(repr(list_value[idx]))
                
            str_type = str_type.lstrip(",")
            str_field = str_field.lstrip(",")
            sql = u"insert into `{0}`({1}) values ({2})".format(tb_name, str_field, str_type);
            iRet = self.execute(sql, list_value)
                    
        
        else:
            pass
            str_field = u'';
            str_value = u'';
            #str_type  = ''
            
            for idx in range(len(list_field)):
                pass
                str_field += u",`{0}`".format(list_field[idx])
                str_value += u",'{0}'".format(list_value[idx])
                #str_type += ",'{0}'".format("?")
                #list_value[idx] = MySQLdb.escape_string(repr(list_value[idx]).decode('utf-8')) #这里使用str 失败 str是类型 repr会新建字符串 然后
                
            str_value = str_value.lstrip(",")
            str_field = str_field.lstrip(",")
           
            sql = u"insert into `{0}`({1}) values ({2})".format(tb_name, str_field, str_value);
            #print list_value;
            #print sql;
            #sys.exit(0)
            
            iRet = self.execute(sql)        
         
        self.commit()   
        return iRet
    
    #同时插入多条语句
    def insert_multi(self, tb_name, list_field, list_list_value):
        pass
        str_value = u''
        str_field = u''
        
        for list_value in list_list_value:
            if len(list_value) != len(list_field):
                raise Exception(u"len of list_field not equal list_value !", list_field, list_value) #优化阶段应该考虑自定义的异常类
            str_value += u"(";
            for value in list_value:
                str_value += u"'{0}',".format(value)
            str_value = str_value.rstrip(",");
            str_value += u")";
            
        for field in  list_field:
            str_field += u"`{0}`,".format(field)
        
        str_field = str_field.rstrip(",")
        
        sql = u"insert into `{0}`({1}) values ({2})".format(tb_name, str_field, str_value)
        iRet= self.execute(sql)
        
        self.commit()
        return iRet
            
    
    #析构函数
    def __del__(self):
        pass
        try:
            
            self.close()
        except Exception as ex:
            print ex
            raise Exception(u"__del__ error !", ex)
    
        
    def begin(self):
        pass
        return self.connect()
    def commit(self):
        pass 
        return self._conn.commit()
    
    def rollback(self):
        pass
        return self._conn.rollback()
    
    def getLastInsertId(self):
        return self._cur.lastrowid
    
    def rowcount(self):
        return self._cur.rowcount
    
    def close(self):
        if self._cur is not None: #表示调用过connect
            self._cur.close()
        if self._conn is not None:
            self._conn.close()
        
        
if __name__ == '__main__':
    #测试
    try:
        import sys
        print sys.path
        if '..' not in sys.path:
            sys.path.append('..')
        import ConfigParser
        import os
        config = ConfigParser.ConfigParser();
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        conf_file = os.path.join(base_path, "confs/dev.ini")
        print conf_file
        print config.read(conf_file) #返回读取的文件 全路径 conf_file 列表
        
        hosts =   config.get('db', 'hosts').split(",")
        print hosts
        print type(hosts) #str,str 字符串类型(123...,113)
        port  = config.get('db', 'port')
        username = config.get('db', 'username')
        password = config.get('db', 'password')
        dbname   = config.get('db', 'dbname')
        obj_mysql = CMysql(hosts = hosts, port = port, username = username, password = password, dbname = dbname)
        obj_mysql.connect()
        tuple_row =  obj_mysql.fetch_one('select * from `user`')
        for val in tuple_row:
            print val
            
        #插入测试
        #iRet = obj_mysql.insert('region2', ()
    except Exception as ex:
        print u"Exception :{0}".format(ex)
    
    