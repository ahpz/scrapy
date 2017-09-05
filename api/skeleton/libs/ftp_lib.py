# -*- coding: utf-8 -*-
#ftp 文件上传模块

__author__ = 'pengzhi'  
__mail__ = 'pengzhi@baidu.com'  
__date__ = '2016-08-09'  
__version = 1.0  
  
#标准库
#第三方库
#应用程序自有库 
#且没行一个
import sys  
import os  
import json  
import ftplib
from ftplib import FTP  
from ftplib import error_perm
_XFER_FILE = 'FILE'  
_XFER_DIR = 'DIR'  
#ClassName, ExceptionName

#GLOBAL_CONSTANT_NAME, CLASS_CONSTANT_NAME,

#module_name, package_name, method_name, function_name, global_var_name, instance_var_name, function_parameter_name, local_var_name

#_InternalClassName, _INTERNAL_CONSTANT_NAME, _internal_function_name, _protected_member_name, __private_member_name
class CFtp(object):  
    ''''' 
    @note: upload local file or dirs recursively to ftp server 
    '''  
    def __init__(self, ip = None, uname = None, pwd = None, port = 21, timeout = 60):  
        self._ftp = None  
        self.set_ftp_params(ip, uname, pwd, port, timeout)
      
    def __del__(self):  
        pass  
        self.clear_env()
      
    def set_ftp_params(self, ip, uname, pwd, port = 21, timeout = 60):          
        self._ip = ip  
        self._uname = uname  
        self._pwd = pwd  
        self._port = port  
        self._timeout = timeout  
      
    def init_env(self):  
        if self._ftp is None:  
            self._ftp = FTP()  
            print '### connect ftp server: %s ...'%self._ip  
            self._ftp.connect(self._ip, self._port, self._timeout)  
            self._ftp.login(self._uname, self._pwd)   
            print self._ftp.getwelcome()  
      
    def clear_env(self):  
        if self._ftp:  
            self._ftp.close()  
            print '### disconnect ftp server: %s!'%self._ip   
            self._ftp = None  
      
    def upload_dir(self, localdir= u'./', remotedir= u'./'):  
        if not os.path.isdir(localdir):    
            #raise Exception(u'The localdir is not directory!', localdir)
            os.makedirs(localdir)
        self.init_env() #可以直接调用此函数
        
        
        self._ftp.cwd(remotedir)   
        for file in os.listdir(localdir):  
            src = os.path.join(localdir, file)  
            if os.path.isfile(src):  
                self.upload_file(src, file)  
            elif os.path.isdir(src):  
                try:    
                    self._ftp.mkd(file)    
                except:    
                    #sys.stderr.write('the dir is exists %s'%file) 
                    raise Exception(u'The dir is exists!', file)
                self.upload_dir(src, file)  
        self._ftp.cwd('..')  
      
    
        
        
    def upload_file(self, localpath, remotepath= u'./'):  
        if not os.path.isfile(localpath):    
            #return  
            raise Exception(u'The localpath is not file!', localpath)
        self.init_env() #可以直接调用此函数
        print '+++ upload %s to %s:%s'%(localpath, self._ip, remotepath)  
        bufsize = 1024
        mixRet = self._ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))  
        print mixRet
      

        
    def __filetype(self, src):  
        if os.path.isfile(src):  
            index = src.rfind('\\')  #window
            if index == -1:  
                index = src.rfind('/')      #linux            
            return _XFER_FILE, src[index+1:]  
        elif os.path.isdir(src):  
            return _XFER_DIR, ''          
      
    def upload(self, src, dest = u'./'):  
        filetype, filename = self.__filetype(src)  
        
        self.init_env()  
        if filetype == _XFER_DIR:  
            self.src_dir = src              
            self.upload_dir(self.src_dir, dest)  
        elif filetype == _XFER_FILE:  
            dest = os.path.join(dest, filename) #组成远程文件名称
            self.upload_file(src, dest)  
        self.clear_env()   
        
                 
    #下载目录 
    def download_dir(self, remotedir = u'./', localdir = u'./'):
        pass
        if not os.path.isdir(localdir):
            #raise Exception(u'The localdir is not directory!', localdir);
            os.makedirs(localdir)   #保证远程空目录也能正常下载
            
        self.init_env() #可以直接调用此函数
        self._ftp.cwd(remotedir)
        print "+++ cmd "+remotedir
        ftp_files = self._ftp.nlst()
        for file in ftp_files:
            local_file = os.path.join(localdir, file)
            if self._is_ftp_dir(file):
                self.download_dir(file, local_file)
                self._ftp.cwd('..')
            else:
                self.download_file(file, local_file) 
            
    #下载文件
    def download_file(self, remotepath, localpath):
        pass
        self.init_env() #可以直接调用此函数
        print '+++ download %s:%s to %s'%(self._ip, remotepath, localpath)
        bufsize = 1024
        
        fp = open(localpath, 'wb')
      
        mixRet = self._ftp.retrbinary(u'RETR ' + remotepath, fp.write)
        print mixRet
        fp.close()    
    
    
    def download(self, dest, src = u'./'):
        pass
        #仿照upload实现
        self.init_env()
        dest = dest.rstrip('/')
        if self._is_ftp_dir(dest):
            #目录下载
            if not os.path.isdir(src):
                #raise Exception(u'The localdir is not directory!', localdir);
                os.makedirs(src)
            self.download_dir(dest, src)
        elif self.is_ftp_file(dest):
            #文件下载
            if os.path.isdir(src):
                src = os.path.join(src, os.path.basename(dest)) #默认 本地文件名和远程远程文件名保持一致
            self.download(dest, src)
            
        else:
            raise Exception(u'The dest is not file or dir!', dest)
         
        self.clear_env()
         
    def _is_ftp_file(self,ftp_path):
        try:
            if ftp_path in self._ftp.nlst(os.path.dirname(ftp_path)):
                return True
            else:
                return False
        except ftplib.error_perm,e:
            return False    
    #判断当前目录是否是目录
    #在上层目录执行 list命令 判断 ls 命令 首字母是否是 d 开头 表示目录
    def _is_ftp_dir(self, ftp_path):
        ftp_path = ftp_path.rstrip('/')
        ftp_parent_path = os.path.dirname(ftp_path)
        self.__ftp_dir_name = os.path.basename(ftp_path)
       
        
        self._is_dir = False
        if ftp_path == '.' or ftp_path== './' or ftp_path=='':
            self._is_dir = True
        else:
          #this ues callback function ,that will change _is_dir value
            try:
                self._ftp.retrlines('LIST %s' %ftp_parent_path,self._ftp_list)
            except ftplib.error_perm,e:
                self._is_dir = False   
        return self._is_dir    
    def _ftp_list(self, line):
        #-rw-r--r--   1 pay      pay          4403 Aug  9 20:54 ftp_lib.py
        
        list = line.split(' ')
        if self.__ftp_dir_name==list[-1] and list[0].startswith('d'):
            self._is_dir = True  

    def delete_file(self, remotefile):
        pass
        self._ftp.delete(remotefile)
        
    def delete_dir(self, remotedir):
        pass
        self._ftp.cwd(remotedir)
        ftp_files = self._ftp.nlst()
                              
        for file in ftp_files:
            pass
            print file
            if self._is_ftp_dir(file):
                #self._ftp.cwd(file)
                self.delete_dir(file)
                self._ftp.cwd('..')
                #print file
                self._ftp.rmd(file)
            elif self._is_ftp_file(file):
                self.delete_file(file)
        
        
    def delete(self, remotepath):
        #删除远程目录下所有文件 或者直接删除 远程 文件
        pass
        self.init_env();
        if self._is_ftp_dir(remotepath):
            #删除目录下所有文件 注意不删除当前目录
            
            self.delete_dir(remotepath)
        elif self._is_ftp_file(remotepath):
            #删除远程文件
            self.delete_file(remotepath)
            
        else:
            raise Exception(u"The remotepath is not file and dir!", remotepath)
        self.clear_env()
if __name__ == '__main__':  
    try:
        src_dir = r"./"  
        src_file = r'ftp_lib.py'  
        xfer = CFtp()  
        xfer.set_ftp_params(u'st01-pay-bi03.st01', 'pay', 'walletbirdsys') 
        dest = u'/home/pay/external_datashare/KUAJING/'
        #xfer.upload(src_dir, dest)      
        #xfer.upload(src_file, dest)  #远程目录 本地文件
        
        #dest = dest + u'ftp_lib.py'
        src = u'./tmp'
        #xfer.download(dest, src)#远程文件 本地文件
        #xfer.download(dest,src)
        #xfer.init_env()
        #print xfer._is_ftp_dir(dest)
        
        #xfer.delete(dest) 测试通过
    except Exception as ex:
        print ex