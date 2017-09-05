# -*- coding: utf-8 -*-
# 网络请求模块

import base64
import urllib
import urllib2
import time
import sys

class CBrowser(object):
  '''
  This class use to set and request the http, and get the info of response.
  e.g. set Authorization Type, request tyep..
  e.g. get html content, state code, cookie..
  SendRequest('http://10.75.0.103:8850/2/photos/square/type.json', 
              data='source=216274069', type='POST', auth='base',
			  user='zl2010', password='111111')
  '''
  def __init__(self, url, data=None, type='GET', auth=None, user=None, password=None, cookie = None, **kwargs):
    '''
    url:request, raise error if none
    date: data for post or get, must be dict type
    type: GET, POST
    auth: option, if has the value must be 'base' or 'cookie'
    user: user for auth
    password: password for auth
    cookie: if request with cookie 
    other header info: 
    e.g. referer='www.sina.com.cn'    
    '''
    self.url = url
    self.data = data
    self.type = type
    self.auth = auth
    self.user = user
    self.password = password 
    self.cookie = cookie 
    
    if 'headers' in kwargs:
      self.headers = kwargs['headers']
    else:
      self.headers = {}
    
    self.setup_request()
    self.send_request()	

  def setup_request(self):
    '''
    setup a request 
    '''
    #print "setup"
    if self.url == None or self.url == '':
      raise u'The url should not empty!'
  
    # set request type 
    #print self.url
    #print self.type
    #print self.data
    #print self.auth
    #print self.user
    #print self.password  
    if self.type == 'POST':	
      self.Req = urllib2.Request(self.url, self.data)
    elif self.type == 'GET':
      if self.data == None:
          self.Req = urllib2.Request(self.url)
      else:
          print self.url + '?' + self.data
          self.Req = urllib2.Request(self.url + '?' + self.data)
    else:
      raise u'The http request type NOT support now!'
    
    ##set auth type 
    if self.auth == 'base':
      if self.user == None or self.password == None:
        raise 'The user or password was not given!'
      else:
        auth_info = base64.encodestring(self.user + ':' + self.password).replace('\n','')
        auth_info = 'Basic ' + auth_info 
        #print auth_info		
        self.Req.add_header("Authorization", auth_info)
    elif self.auth == 'cookie':
      if self.cookie == None:
        raise 'The cookie was not given!'
      else:
        self.Req.add_header("Cookie", self.cookie) 
    else:
      pass    ##add other auth type here 

    ##set other header info 
    
    #if self.referer:
    #  self.Req.add_header('referer', self.referer)
    #if self.user_agent:
    # self.Req.add_header('user-agent', self.user_agent)
    for k in self.headers.keys():
      pass
      self.Req.add_header(k, self.headers[k])
    
    #print self.Req.header_items()
   
      
  def send_request(self):  
    '''
    send a request 
    '''
    # get a response object 
    
    try:
      self.Res = urllib2.urlopen(self.Req)
      self.source = self.Res.read()
      self.goal_url = self.Res.geturl()
      self.code = self.Res.getcode()
     
      
      self.head_dict = self.Res.info().dict
     
      self.Res.close()
    except urllib2.HTTPError, e:
      self.code = e.code
      print u"[{0}:{1}] Exception:{2}".format(os.path.basename(__file__), sys._getframe().f_lineno, e.args)      #print e
        


  def get_code(self):
    return self.code
    
  def get_url(self):
    return self.goal_url
    
  def get_source(self):        
    return self.source
    
  def get_header_info(self):
    return self.head_dict

  def get_cookie(self):
    if 'set-cookie' in self.head_dict:
      return self.head_dict['set-cookie']
    else:
      return None    
      
  def get_content_type(self):
    if 'content-type' in self.head_dict:
      return self.head_dict['content-type']
    else:
      return None
    
  def get_expires_time(self):
    if 'expires' in self.head_dict:
      return self.head_dict['expires']
    else:
      return None    
    
  def get_server_name(self):
    if 'server' in self.head_dict:
      return self.head_dict['server']
    else:
      return None   
      
  def __del__(self):
    pass   

__all__ = [CBrowser,]
      
if __name__ == '__main__':
  '''
  The example for using the SendRequest class 
  '''
  value = {'source':'216274069'}
  data = urllib.urlencode(value)
  url = 'http://10.75.0.103:8850/2/photos/square/type.json'
  user = 'wz_0001'
  password = '111111'
  auth = 'base'
  type = 'POST'
  t2 = time.time()
  rs = CBrowser('http://www.baidu.com')
  #rs = SendRequest(url, data=data, type=type, auth=auth, user=user, password=password)
 # print 't2: ' + str(time.time() - t2)
  print '---------------get_code()---------------'
 # print rs.get_code()
  print '---------------get_url()---------------'
  #print rs.get_url()
  print '---------------get_source()---------------'
  #print rs.get_source()
  print '---------------get_cookie()---------------'
  print rs.get_cookie()
  rs = None