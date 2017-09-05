# -*- coding: utf-8 -*-
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  
import smtplib 
import os
import sys
#https://docs.python.org/3/library/email.mime.html
#邮件内容也属于附件的
class CEmail:
    # 构造函数：初始化基本信息
    def __init__(self, host, user, passwd):
        lInfo = user.split("@")
        self._user = user
        self._account = lInfo[0]
        self._me = self._account + "<" + self._user + ">" 
        server = smtplib.SMTP()  
        server.connect(host)  
        server.login(self._account, passwd)
        self._server = server      
        self.__init_info();#
        
        

    
    def __init_info(self):
        self._to = []
        self._cc = []
        self._bcc= []
        self._attachements = []    
        
        self._body = ''#邮件内容
        self._subject  = '';#邮件主题
        self._subtype = 'html'#默认html格式
        
    
        
    def add_address(self, addr):
        pass
        self._to.append(addr)
    def clear_addresses(self):
        pass
        self._to = []

   
    #添加抄送邮件人
    def add_cc(self, addr):
        pass
        self._cc.append(addr)
    #清除抄送邮件人
    def clear_cces(self):
        pass
        self._cc = []
    
    def add_bcc(self, addr):
        self._bcc.append(addr)
    def clear_bcces(self):
        self._bcc = []
    #增加附件文件
    #type :Content-type:
    def add_attachement(self, filename, name = u'', encoding = u'base64', type = u'', disposition = u'attachment'):
        pass
        if False == os.path.isfile(filename):
            raise Exception(u"The filename is not valid!", filename)
        if u'' ==  name:
            (name,ext) = self.__get_filename_and_ext(filename)
            
        if u'' == type:
            type = self.__filename_to_type(filename)
        
        attachment = {
            u"filename":filename, 
            u"name":name,
            u"encoding":encoding, 
            u"type":type,
            u"disposition":disposition,
        }
        self._attachements.append(attachment)
        
    def clear_attachements(self):
        pass
        self._attachments = []
    
    
    @property
    def body(self):
        return self._body;
    
    @body.setter
    def body(self, value):
        self._body = value
    @body.deleter
    def body(self):
        del self._body;
        
    @property
    def subtype(self):
        return self._subtype;
    @subtype.setter
    def subtype(self, value):
        self._subtype = value
    @subtype.deleter
    def subtype(self):
        del self._subtype;
    
    @property
    def subject(self):
        return self._subject;
    @subject.setter
    def subject(self, value):
        self._subject = value
    @subject.deleter
    def subject(self):
        del self._subject;
    
    def __pre_send(self):
        if len(self._attachements) > 0:
            msg = MIMEMultipart()  
            for attach in self._attachements: 
                filename = attach[u'filename']
                att = MIMEText(open(filename,'rb').read(), attach[u'encoding'], 'utf-8')
                att.add_header(u'Content-Disposition', u'{0};filename={1}'.format(attach[u'disposition'], attach[u'name']))
                att.add_header(u'Content-Type',attach[u'type']);#image/jpeg | application/octet-stream
                msg.attach(att)
                
            msg.attach(MIMEText(self.body, _subtype=self.subtype, _charset='utf-8'))
            msg['Subject'] = self.subject
            msg['From']    = self._me  
            msg['To']      = ";".join(self._to)
            if len(self._cc) > 0:
                msg['CC']      = ";".join(self._cc)
            if len(self._bcc) > 0:
                msg['BCC']     = ";".join(self._bcc)
            return msg.as_string();
        else:
            #木有附件的邮件
            msg = MIMEText(self.body, _subtype=self.subtype, _charset='utf-8')  
            msg['Subject'] = self.subject #属性只能这么访问
            msg['From']    = self._me  
            msg['To']      = ";".join(self._to)
            if len(self._cc) > 0:
                msg['CC']      = ";".join(self._cc)
            if len(self._bcc) > 0:
                msg['BCC']     = ";".join(self._bcc)  
            
            
           
            #print msg.as_string()
            return msg.as_string();
    #subtype = html|plan html或者文本邮件
    def sendEmail(self):
        pass
        msg = self.__pre_send();
        try:
            return self._server.sendmail(self._me, self._to, msg) #senderror
        except Exception as e:
            print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, e.args) 
            raise Exception("sendMail error!", e.args);
        
    def __filename_to_type(self, filename):
        pass
        import os
        l_ret = os.path.splitext(filename) # a ('a', '') a.txt ('a','.txt')
        ext   = l_ret[1].lstrip('.')
        return self.__mime_types(ext)
        
    
    def __mime_types(self,ext = ''):
        mimes = {
            'xl'  :'application/excel',
            'js'  :'application/javascript',
            'hqx' :'application/mac-binhex40',
            'cpt' :'application/mac-compactpro',
            'bin' :'application/macbinary',
            'doc' :'application/msword',
            'word':'application/msword',
            'class':'application/octet-stream',
            'dll' :'application/octet-stream',
            'dms' :'application/octet-stream',
            'exe' :'application/octet-stream',
            'lha' :'application/octet-stream',
            'lzh' :'application/octet-stream',
            'psd' :'application/octet-stream',
            'sea' :'application/octet-stream',
            'so'  :'application/octet-stream',
            'oda' :'application/oda',
            'pdf' :'application/pdf',
            'ai'  :'application/postscript',
            'eps' :'application/postscript',
            'ps'  :'application/postscript',
            'smi' :'application/smil',
            'smil':'application/smil',
            'mif' :'application/vnd.mif',
            'xls' :'application/vnd.ms-excel',
            'ppt' :'application/vnd.ms-powerpoint',
            'wbxml':'application/vnd.wap.wbxml',
            'wmlc':'application/vnd.wap.wmlc',
            'dcr' :'application/x-director',
            'dir' :'application/x-director',
            'dxr' :'application/x-director',
            'dvi' :'application/x-dvi',
            'gtar':'application/x-gtar',
            'php3':'application/x-httpd-php',
            'php4':'application/x-httpd-php',
            'php' :'application/x-httpd-php',
            'phtml':'application/x-httpd-php',
            'phps':'application/x-httpd-php-source',
            'swf' :'application/x-shockwave-flash',
            'sit' :'application/x-stuffit',
            'tar' :'application/x-tar',
            'tgz' :'application/x-tar',
            'xht' :'application/xhtml+xml',
            'xhtml':'application/xhtml+xml',
            'zip' :'application/zip',
            'mid' :'audio/midi',
            'midi':'audio/midi',
            'mp2' :'audio/mpeg',
            'mp3' :'audio/mpeg',
            'mpga':'audio/mpeg',
            'aif' :'audio/x-aiff',
            'aifc':'audio/x-aiff',
            'aiff':'audio/x-aiff',
            'ram' :'audio/x-pn-realaudio',
            'rm'  :'audio/x-pn-realaudio',
            'rpm' :'audio/x-pn-realaudio-plugin',
            'ra'  :'audio/x-realaudio',
            'wav' :'audio/x-wav',
            'bmp' :'image/bmp',
            'gif' :'image/gif',
            'jpeg':'image/jpeg',
            'jpe' :'image/jpeg',
            'jpg' :'image/jpeg',
            'png' :'image/png',
            'tiff':'image/tiff',
            'tif' :'image/tiff',
            'eml' :'message/rfc822',
            'css' :'text/css',
            'html':'text/html',
            'htm' :'text/html',
            'shtml' : 'text/html',
            'log' :'text/plain',
            'text':'text/plain',
            'txt' :'text/plain',
            'rtx' :'text/richtext',
            'rtf' :'text/rtf',
            'vcf' :'text/vcard',
            'vcard' : 'text/vcard',
            'xml' :'text/xml',
            'xsl' :'text/xml',
            'mpeg':'video/mpeg',
            'mpe' :'video/mpeg',
            'mpg' :'video/mpeg',
            'mov' :'video/quicktime',
            'qt'  :'video/quicktime',
            'rv'  :'video/vnd.rn-realvideo',
            'avi' :'video/x-msvideo',
            'movie':'video/x-sgi-movie'                    
        }
        if mimes.has_key(ext):
            return mimes.get(ext)
        else:
            return 'application/octet-stream'
        
    def __get_filename_and_ext(self,filename):
        import os
        (filepath,tempfilename) = os.path.split(filename);
        (shotname,extension) = os.path.splitext(tempfilename);
        return shotname,extension    

    
    def __del__(self):
        self._server.quit()
        self._server.close()

if __name__ == "__main__":
    try:
        
        
        mailto_list = ['940251401@qq.com','pengzhi@baidu.com'] 
        
        mail = CEmail('smtp.163.com', 'hzkuajing@163.com', 'hzkuajing123456')
        mail.subject = '测试邮件'
 
        mail.body = 'Test<p>a</p>';
        mail.add_address('940251401@qq.com')
        mail.add_cc('pengzhi@baidu.com')
        mail.subtype = 'plain';#Test<p>a</ap> 若为html Test 换行 a
        mail.add_attachement("log_lib.py")
        mail.add_attachement('banner.jpg')
        mail.sendEmail();
    except Exception as ex:
        print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, ex.args)
    
    #if mail.sendTxtMail(mailto_list, "测试邮件", "hello world！<br><br><h1>你好，发送文本文件测试<h1>"):  
        #print "发送成功"  
    #else:  
        #print "发送失败"
    
    #if mail.sendAttachMail(mailto_list, "测试邮件-带两个附件", "hello world！<br><br><h1>你好，发送文本文件测试<h1>"):  
        #print "发送成功"  
    #else:  
        #print "发送失败"
    
    #if mail.sendImageMail(mailto_list, "测试邮件-带一个图片的附件", "hello world！<br><br><h1>你好，发送文本文件测试<h1>"):  
        #print "发送成功"  
    #else:  
        #print "发送失败"