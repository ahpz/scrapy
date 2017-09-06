# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import types
import signal
import twitter  #pip install twitter pip install python-twitter
import urllib2  #需要安装代理 才可以访问外网
import commands
import requests
import argparse
import threading

from urllib2 import URLError, HTTPError

from skeleton.bootstrap import Env
from skeleton.libs.threadpool_lib import CThreadPool

"""账号密钥 twitter申请开发者账号即可"""
CONSUMER_KEY       = 'xxxxx'
CONSUMER_SECRET    = 'xxxxx'
OAUTH_TOKEN        = 'xxxxxx'
OAUTH_TOKEN_SECRET = 'xxxxxx'
"""下载视频或者图片"""
def download(url, file_path):
    with open(file_path, 'wb') as file:
        sys.stdout.write("Downloading %s \n" % os.path.basename(file_path))
        bytes = requests.get(url).content
        file.write(bytes)
        
def sig_handler(sig, frame):   
    sys.stdout.write('receive a signal %d \n' % (sig))
    sys.exit(0)
    
class TwitterCrawler(object):
    def __init__(self, screen_name = u'Eastbay'):
        auth             = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
        self.api         = twitter.Twitter(auth=auth)
        self.thread_pool = CThreadPool()
        self.screen_name = screen_name #搜索用户名
        self.save_dir    = os.path.join(Env.base_path, u'data/twitter', self.screen_name.replace(' ',''), time.strftime("%Y%m%d", time.localtime()))
        self.max_num     = 100 #测试阶段
        
    def __del__(self):
        self.thread_pool.close() #优雅关闭多线程
           
    def stop(self):
        self.thread_pool.close()
        
    def is_over(self):
        if 0 == self.thread_pool.thread_num():
            return True
        return False    
    
    """异步多线程下载图片"""
    def async_start(self):
        if False == os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        items = self.crawl()
        sys.stdout.write("count of items:{0}\n".format(len(items)))
        """多线程下载视频 + 图片"""
        filename = os.path.join(self.save_dir, 'results')
        fp = open(filename, 'w')
        for item in items:
            url = item['image_url'];
            base_name = url.split('/')[-1]
            file_path = os.path.join(self.save_dir, base_name) #多线程下载存储本地文件
            item['image_filepath'] = file_path
            args  = (url, file_path) #待验证 多线程 是否可以恨自己访问当前类的 变量 应该可以
            self.thread_pool.run(download, args = args) #线程池添加job    
           
            if 'video' == item['type']:
                url = item['video_url'];
                base_name = url.split('/')[-1]
                file_path = os.path.join(self.save_dir, base_name) #多线程下载存储本地文件
                item['video_filepath'] = file_path
                args  = (url, file_path) #待验证 多线程 是否可以恨自己访问当前类的 变量 应该可以
                self.thread_pool.run(download, args = args) #线程池添加job    
            fp.write(json.dumps(items) + '\n') #本地文件存储
        fp.close()
        
    """https://dev.twitter.com/rest/reference/get/statuses/user_timeline"""
    def crawl(self, items = [], max_id = None):
        """
        include_rts:include retweets 
        """
        if max_id is not None:
            tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,include_rts=1, count=20,max_id = max_id)
        else:
            tweets = self.api.statuses.user_timeline(screen_name=self.screen_name,count=20,include_rts=1)
        for tweet in tweets:
            Env.get_logger().debug("tweet:{0}".format(json.dumps(tweet)))
            item = {}
            item['id']   = tweet['id_str']
            item['text'] = tweet.has_key('full_text') and tweet['full_text'] or "-"
            item['created_time']   = tweet['created_at']
            item['like_count']     = tweet['favorite_count'] #喜欢数
            item['retweet_count']  = tweet['retweet_count']  #被转发次数  
            if not tweet.has_key('extended_entities') or 1 != len(tweet['extended_entities']['media']):
                Env.get_logger().warning("Not has extended_entities or extended_entities.media more than one.")
                Env.output("Not has extended_entities or extended_entities.media more than one")
                Env.get_logger().warning("item:{0}".format(json.dumps(item)))
                continue;
            media = tweet['extended_entities']['media'][0]
            if u'video' != media['type'] and u'photo' != media['type']:
                Env.output("The type not photo or video.")
                Env.get_logger().warning("The type not photo or video.")
                Env.get_logger().warning("item:{0}".format(json.dumps(item)))
                continue
            """图片是始终存在的"""
            item['type']  = media['type'] #photo or video
            item['image_url'] = media['media_url'] #图片 or 视频背景图片
            if 'video' == media['type']:
                #筛选 mp4 格式 m3u8
                for variant in media['video_info']['variants']:
                    if u'video/mp4' == variant[u'content_type']:
                        item['video_url'] = variant['url'] #保证是mp4格式非m3u8
                        items.append(item)
                        break;
            else:
                items.append(item)
        if self.max_num < len(items) or not len(tweets):
            return items
        else:
            """递归查询下一页数据"""
            max_id = tweets[-1]['id_str']
            return self.crawl(items, max_id = max_id)
            
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('screen_name', default="Easybay")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, sig_handler)  
    signal.signal(signal.SIGINT, sig_handler)     
    """注意 父进程会挂起等待子线程结束 因为子线程未设置setdaemon"""    
    try:
        twitt = TwitterCrawler(args.screen_name)
        twitt.async_start()
        twitt.stop()
    except HTTPError as e:
        Env.get_logger().warning("The server couldn\'t fulfill the request| code:{0}".format(e.code))
        Env.output("The server couldn\'t fulfill the request| code:{0}".format(e.code))
    except URLError as e:  
        Env.get_logger().warning('We failed to reach a server | url :{0} | reason:{1}'.format(url, e.reason));  
        Env.output('We failed to reach a server | url :{0} | reason:{1}'.format(url, e.reason))
    except Exception as e:
        Env.get_logger().warning("exception : {0}".format(repr(e)))
        Env.output("exception :{0}".format(repr(e)))
    else:
        while twitt.is_over():
            """保证主线程不挂起 可以处理信号"""
            time.sleep(1)        
        Env.get_logger().info("twitter download success.")
        Env.output("twitter download success.");    
